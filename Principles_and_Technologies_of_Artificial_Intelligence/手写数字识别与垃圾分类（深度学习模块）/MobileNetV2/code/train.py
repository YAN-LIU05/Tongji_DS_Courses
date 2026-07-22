# Copyright 2020 Huawei Technologies Co., Ltd
# Licensed under the Apache License, Version 2.0

import os
import time
import random
import numpy as np
import matplotlib.pyplot as plt
import string

from mindspore import Tensor
from mindspore import nn
from mindspore.nn import WithLossCell, TrainOneStepCell
from mindspore.nn.optim.momentum import Momentum
from mindspore.nn.loss import SoftmaxCrossEntropyWithLogits
from mindspore.common import dtype as mstype
from mindspore.communication.management import get_rank
from mindspore.train.model import Model
from mindspore.train.loss_scale_manager import FixedLossScaleManager
from mindspore.train.serialization import save_checkpoint
from mindspore.common import set_seed
from mindspore.nn import Accuracy
from sklearn.manifold import TSNE
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay

from src.dataset import create_dataset, extract_features
from src.lr_generator import get_lr
from src.config import set_config
from src.args import train_parse_args
from src.utils import context_device_init, switch_precision, config_ckpoint
from src.models import CrossEntropyWithLabelSmooth, define_net, load_ckpt

plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
set_seed(1)

def evaluate_accuracy(model, dataset):
    acc = model.eval(dataset)
    return acc.get("Accuracy", 0.0)

if __name__ == '__main__':
    args_opt = train_parse_args()
    config = set_config(args_opt)
    start = time.time()

    print(f"train args: {args_opt}\ncfg: {config}")
    context_device_init(config)

    backbone_net, head_net, net = define_net(config, args_opt.is_training)

    if args_opt.pretrain_ckpt != "" and args_opt.freeze_layer == "backbone":
        load_ckpt(backbone_net, args_opt.pretrain_ckpt, trainable=False)
        step_size = extract_features(backbone_net, args_opt.dataset_path, config)
    else:
        if args_opt.platform == "CPU":
            raise ValueError("CPU only support fine tune the head net, doesn't support fine tune the all net")

        if args_opt.pretrain_ckpt:
            load_ckpt(backbone_net, args_opt.pretrain_ckpt)

        dataset = create_dataset(dataset_path=args_opt.dataset_path, do_train=True, config=config)
        val_dataset = create_dataset(dataset_path=args_opt.dataset_path, do_train=False, config=config)
        step_size = dataset.get_dataset_size()

    if step_size == 0:
        raise ValueError("The step_size of dataset is zero.")

    switch_precision(net, mstype.float16, config)

    if config.label_smooth > 0:
        loss = CrossEntropyWithLabelSmooth(
            smooth_factor=config.label_smooth, num_classes=config.num_classes)
    else:
        loss = SoftmaxCrossEntropyWithLogits(sparse=True, reduction='mean')

    epoch_size = config.epoch_size
    lr = Tensor(get_lr(0, config.lr_init, config.lr_end, config.lr_max,
                       config.warmup_epochs, epoch_size, step_size))

    losses_list = []
    accs_list = []
    epochs_record = []

    if args_opt.pretrain_ckpt == "" or args_opt.freeze_layer == "none":
        loss_scale = FixedLossScaleManager(config.loss_scale, drop_overflow_update=False)
        opt = Momentum(filter(lambda x: x.requires_grad, net.get_parameters()), lr,
                       config.momentum, config.weight_decay, config.loss_scale)
        model = Model(net, loss_fn=loss, optimizer=opt, loss_scale_manager=loss_scale, metrics={"Accuracy": Accuracy()})



        cb = config_ckpoint(config, lr, step_size)
        print("============== Starting Training ==============")

        for epoch in range(epoch_size):
            model.train(1, dataset, callbacks=cb, dataset_sink_mode=True)


        print("============== End Training ==============")

    else:
        opt = Momentum(filter(lambda x: x.requires_grad, head_net.get_parameters()), lr,
                       config.momentum, config.weight_decay)
        # opt = nn.Adam(
        #     params=filter(lambda x: x.requires_grad, head_net.get_parameters()),
        #     learning_rate=lr,
        #     weight_decay=config.weight_decay
        # )


        network = WithLossCell(head_net, loss)
        network = TrainOneStepCell(network, opt)
        network.set_train()

        features_path = args_opt.dataset_path + '_features'
        idx_list = list(range(step_size))
        rank = 0
        if config.run_distribute:
            rank = get_rank()

        save_ckpt_path = os.path.join(config.save_checkpoint_path, 'ckpt_' + str(rank) + '/')
        os.makedirs(save_ckpt_path, exist_ok=True)

        for epoch in range(epoch_size):
            random.shuffle(idx_list)
            epoch_start = time.time()
            epoch_losses = []

            for j in idx_list:
                feature = Tensor(np.load(os.path.join(features_path, f"feature_{j}.npy")))
                label = Tensor(np.load(os.path.join(features_path, f"label_{j}.npy")))
                loss_val = network(feature, label).asnumpy()
                epoch_losses.append(loss_val)

            mean_loss = np.mean(epoch_losses)
            losses_list.append(mean_loss)

            epoch_mseconds = (time.time() - epoch_start) * 1000
            per_step_mseconds = epoch_mseconds / step_size
            print(f"epoch[{epoch+1}/{epoch_size}], iter[{step_size}] cost: {epoch_mseconds:.3f}, "
                  f"per step time: {per_step_mseconds:.3f}, avg loss: {mean_loss:.3f}")
            

            if (epoch + 1) % 10 == 0:
                print(f"===== Eval at epoch {epoch + 1} =====")
                net.set_train(False)
                eval_dataset = create_dataset(dataset_path='./data_new', do_train=False, config=config)
                eval_model = Model(net, loss_fn=loss, metrics={'Accuracy': Accuracy()})
                eval_result = eval_model.eval(eval_dataset)

                acc_val = eval_result.get("Accuracy", 0.0)
                accs_list.append(acc_val)
                epochs_record.append(epoch + 1)
                print(f"Epoch {epoch + 1} eval result: {eval_result}")

                # 提取特征用于t-SNE与混淆矩阵
                all_features = []
                all_labels = []
                all_preds = []

                for data in eval_dataset.create_dict_iterator():
                    image = data['image']
                    label = data['label'].asnumpy()
                    feature = net(image).asnumpy()  # 输出应为 logits
                    pred = np.argmax(feature, axis=1)

                    all_features.append(feature)
                    all_labels.extend(label)
                    all_preds.extend(pred)

                features = np.concatenate(all_features, axis=0)
                labels = np.array(all_labels)
                preds = np.array(all_preds)

                # ===== t-SNE 可视化 =====
                tsne = TSNE(n_components=2, random_state=0)
                tsne_result = tsne.fit_transform(features)

                # 设置颜色映射：使用 nipy_spectral 获取26种颜色
                colors = plt.cm.get_cmap('nipy_spectral', 26)
                class_names = list(string.ascii_uppercase)  # ['A', 'B', ..., 'Z']

                plt.figure(figsize=(10, 8))

                # 按类绘制散点
                for i in range(26):
                    idx = labels == i
                    plt.scatter(tsne_result[idx, 0], tsne_result[idx, 1],
                                c=[colors(i)], label=class_names[i], s=10)

                plt.title(f"t-SNE Visualization at Epoch {epoch + 1}")
                plt.grid(True)

                # 设置图例
                plt.legend(title="Classes", bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
                plt.tight_layout()
                plt.savefig(f"tsne_epoch_{epoch+1}.png")
                plt.close()

                # ===== 混淆矩阵绘制 =====
                cm = confusion_matrix(labels, preds)
                disp = ConfusionMatrixDisplay(confusion_matrix=cm)
                disp.plot(cmap=plt.cm.Blues, xticks_rotation=45)
                plt.title(f"Confusion Matrix at Epoch {epoch + 1}")
                plt.savefig(f"confusion_matrix_epoch_{epoch+1}.png")
                plt.close()

                net.set_train(True)



            if (epoch + 1) % config.save_checkpoint_epochs == 0:
                save_checkpoint(net, os.path.join(save_ckpt_path, f"mobilenetv2_{epoch+1}.ckpt"))

        print("total cost {:.4f} s".format(time.time() - start))

    # ========== 保存可视化图像 ==========
    if losses_list:
        plt.figure()
        plt.plot(range(1, len(losses_list) + 1), losses_list, label="Loss")
        plt.xlabel("Epoch")
        plt.ylabel("Loss")
        plt.title("Training Loss Curve")
        plt.legend()
        plt.grid()
        plt.savefig("loss_curve.png")
        plt.close()

    if accs_list:
        plt.figure()
        plt.plot(epochs_record, accs_list, label="Accuracy", color="green")
        plt.xlabel("Epoch")
        plt.ylabel("Accuracy")
        plt.title("Validation Accuracy (every 10 epochs)")
        plt.legend()
        plt.grid()
        plt.savefig("acc_curve.png")
        plt.close()

    # ========== 保存CSV记录 ==========
    import csv
    with open("metrics.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Epoch", "Loss", "Accuracy"])
        for i, ep in enumerate(epochs_record):
            loss_val = losses_list[ep - 1] if ep - 1 < len(losses_list) else ""
            acc_val = accs_list[i]
            writer.writerow([ep, loss_val, acc_val])


