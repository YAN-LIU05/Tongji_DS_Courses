import os
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
import gzip
import shutil
import mindspore as ms
import mindspore.nn as nn
from mindspore.dataset import vision, transforms
from mindspore.dataset import MnistDataset

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

class LeNet5(nn.Cell):
    def __init__(self):
        super(LeNet5, self).__init__()
        self.conv1 = nn.Conv2d(1, 6, 5, pad_mode='valid')  # 输出: (24, 24, 6)
        self.conv2 = nn.Conv2d(6, 16, 5, pad_mode='valid') # 输出: (8, 8, 16)
        # 计算展平后的特征维度：16 * 4 * 4 = 256
        self.fc1 = nn.Dense(256, 120)  # 修改输入维度为 256
        self.fc2 = nn.Dense(120, 84)
        self.fc3 = nn.Dense(84, 10)
        self.relu = nn.ReLU()
        self.max_pool2d = nn.MaxPool2d(kernel_size=2, stride=2)
        self.flatten = nn.Flatten()

    def construct(self, x):
        # 输入 x: (batch_size, 1, 28, 28)
        x = self.conv1(x)                    # -> (batch_size, 6, 24, 24)
        x = self.relu(x)
        x = self.max_pool2d(x)              # -> (batch_size, 6, 12, 12)
        x = self.conv2(x)                   # -> (batch_size, 16, 8, 8)
        x = self.relu(x)
        x = self.max_pool2d(x)              # -> (batch_size, 16, 4, 4)
        x = self.flatten(x)                 # -> (batch_size, 256)
        x = self.relu(self.fc1(x))         # -> (batch_size, 120)
        x = self.relu(self.fc2(x))         # -> (batch_size, 84)
        x = self.fc3(x)                    # -> (batch_size, 10)
        return x

def softmax(x):
    e_x = np.exp(x - np.max(x))
    return e_x / np.sum(e_x)


def download_and_extract_mnist(target_dir):
    import urllib.request
    import gzip

    os.makedirs(target_dir, exist_ok=True)
    base_url = "https://ossci-datasets.s3.amazonaws.com/mnist/"
    files = {
        "train-images-idx3-ubyte.gz",
        "train-labels-idx1-ubyte.gz",
        "t10k-images-idx3-ubyte.gz",
        "t10k-labels-idx1-ubyte.gz"
    }

    for file in files:
        file_path = os.path.join(target_dir, file)
        if not os.path.exists(file_path.replace('.gz', '')):
            print(f"正在下载: {file}")
            urllib.request.urlretrieve(base_url + file, file_path)
            with gzip.open(file_path, 'rb') as f_in:
                with open(file_path.replace('.gz', ''), 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            print(f"完成解压: {file}")
        else:
            print(f"{file} 已存在，跳过下载。")

def prepare_mnist_data(data_dir):
    """准备 MNIST 数据集，解压文件并组织到对应目录"""
    # 创建训练和测试目录
    train_dir = os.path.join(data_dir, 'train')
    test_dir = os.path.join(data_dir, 'test')
    os.makedirs(train_dir, exist_ok=True)
    os.makedirs(test_dir, exist_ok=True)

    # 定义文件映射
    file_mapping = {
        'train-images-idx3-ubyte.gz': ('train', 'train-images-idx3-ubyte'),
        'train-labels-idx1-ubyte.gz': ('train', 'train-labels-idx1-ubyte'),
        't10k-images-idx3-ubyte.gz': ('test', 't10k-images-idx3-ubyte'),
        't10k-labels-idx1-ubyte.gz': ('test', 't10k-labels-idx1-ubyte')
    }

    # 解压文件到对应目录
    for gz_file, (subset, extract_name) in file_mapping.items():
        gz_path = os.path.join(data_dir, gz_file)
        if os.path.exists(gz_path):
            target_dir = train_dir if subset == 'train' else test_dir
            target_path = os.path.join(target_dir, extract_name)
            
            if not os.path.exists(target_path):
                print(f"正在解压: {gz_file}")
                with gzip.open(gz_path, 'rb') as f_in:
                    with open(target_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                print(f"解压完成: {gz_file}")


def create_dataset(data_path, batch_size=32, repeat_size=1):
    dataset = MnistDataset(data_path)
    
    transform = [
        vision.Rescale(1.0 / 255.0, 0),
        vision.Normalize([0.1307], [0.3081]),
        vision.HWC2CHW()
    ]
    
    target_transform = transforms.TypeCast(ms.int32)
    
    dataset = dataset.map(operations=transform, input_columns="image")
    dataset = dataset.map(operations=target_transform, input_columns="label")
    dataset = dataset.batch(batch_size)
    dataset = dataset.repeat(repeat_size)
    
    return dataset

def train_model(train_dataset, test_dataset, epochs, if_early_stop=False):
    # 定义网络
    network = LeNet5()
    
    # 定义损失函数和优化器
    net_loss = nn.SoftmaxCrossEntropyWithLogits(sparse=True, reduction='mean')
    net_opt = nn.Momentum(network.trainable_params(), learning_rate=0.01, momentum=0.9)
    
    # 定义训练模型
    model = ms.Model(network, net_loss, net_opt, metrics={'accuracy'})
    
    # 用于记录训练过程
    train_losses = []
    train_accuracies = []
    test_accuracies = []
    
    # 获取总步数用于进度显示
    steps_per_epoch = train_dataset.get_dataset_size()
    
    class ProgressCallback(ms.train.callback.Callback):
        def __init__(self, epochs, steps_per_epoch):
            super().__init__()
            self.pbar = tqdm(total=epochs * steps_per_epoch, 
                           desc='Training', 
                           unit='step')
            
        def step_end(self, run_context):
            self.pbar.update(1)
            
        def epoch_end(self, run_context):
            self.pbar.refresh()
        
        def train_end(self, run_context):
            self.pbar.close()
    
    class CustomCallback(ms.train.callback.Callback):
        def __init__(self, model, test_dataset):
            super().__init__()
            self.model = model
            self.test_dataset = test_dataset
            self.epoch_losses = []
            self.current_epoch = 0
        
        def step_end(self, run_context):
            cb_params = run_context.original_args()
            loss = cb_params.net_outputs.asnumpy()
            self.epoch_losses.append(loss)
        
        def epoch_end(self, run_context):
            self.current_epoch += 1
            # 计算当前epoch的平均损失
            avg_loss = np.mean(self.epoch_losses)
            train_losses.append(avg_loss)
            self.epoch_losses = []
            
            # 计算训练集准确率
            train_metrics = self.model.eval(train_dataset)
            train_accuracies.append(train_metrics['accuracy'])
            
            # 计算测试集准确率
            test_metrics = self.model.eval(test_dataset)
            test_accuracies.append(test_metrics['accuracy'])
            
            # 打印当前epoch的结果
            print(f"\nEpoch [{self.current_epoch}/{epochs}]")
            print(f"损失: {avg_loss:.4f}")
            print(f"训练集准确率: {train_metrics['accuracy']:.4f}")
            print(f"测试集准确率: {test_metrics['accuracy']:.4f}")
    class EarlyStopCallback(ms.train.callback.Callback):
        def __init__(self, patience=5, min_delta=1e-4):
            super().__init__()
            self.patience = patience  # 容忍的epoch数量
            self.min_delta = min_delta  # 最小变化阈值
            self.best_loss = float('inf')
            self.wait = 0
            self.stopped_epoch = 0
            self.should_stop = False

        def epoch_end(self, run_context):
            cb_params = run_context.original_args()
            epoch_loss = np.mean(cb_params.net_outputs.asnumpy())
            
            if epoch_loss < self.best_loss - self.min_delta:
                self.best_loss = epoch_loss
                self.wait = 0
            else:
                self.wait += 1
                if self.wait >= self.patience:
                    self.should_stop = True
                    run_context.request_stop()
                    print(f'\n早停: 验证集损失在 {self.patience} 个epoch内未改善')
                    print(f'最佳损失: {self.best_loss:.4f}')
    
    # 创建回调
    progress_cb = ProgressCallback(epochs, steps_per_epoch)
    custom_cb = CustomCallback(model, test_dataset)
    early_stop_cb = EarlyStopCallback(patience=3)
    if if_early_stop:
        callbacks = [progress_cb, custom_cb, early_stop_cb]
    else:    
        callbacks = [progress_cb, custom_cb]
    
    # 训练模型
    print(f"\n开始训练，共 {epochs} 个 epoch:")
    print(f"早停条件: {early_stop_cb.patience} 个epoch内验证集损失无改善")
    model.train(epochs, train_dataset, callbacks=callbacks)
    
    # 如果发生早停，调整训练历史图表的范围
    if early_stop_cb.should_stop:
        train_losses = train_losses[:early_stop_cb.wait + 1]
        train_accuracies = train_accuracies[:early_stop_cb.wait + 1]
        test_accuracies = test_accuracies[:early_stop_cb.wait + 1]
    
    # 绘制训练过程
    plt.figure(figsize=(12, 4))
    
    # 绘制损失值变化
    plt.subplot(1, 2, 1)
    plt.plot(train_losses, label='训练损失')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.title('训练损失变化')
    plt.legend()
    
    # 绘制准确率变化
    plt.subplot(1, 2, 2)
    plt.plot(train_accuracies, label='训练集准确率')
    plt.plot(test_accuracies, label='测试集准确率')
    plt.xlabel('Epoch')
    plt.ylabel('Accuracy')
    plt.title('准确率变化')
    plt.legend()
    
    plt.tight_layout()
    plt.savefig('training_history.png')
    print("\n训练过程图表已保存为 training_history.png")
    
    return model

def visualize_all_digits(model, test_dataset):
    """可视化所有数字(0-9)的预测结果"""
    images_dict = {}
    predictions_dict = {}
    found_digits = set()

    # 获取测试集数据
    data_iter = test_dataset.create_dict_iterator()

    while len(found_digits) < 10:
        try:
            batch = next(data_iter)
            images, labels = batch['image'], batch['label']

            for i, label in enumerate(labels.asnumpy()):
                digit = int(label)
                if digit not in found_digits:
                    found_digits.add(digit)

                    image = images[i].asnumpy()
                    images_dict[digit] = image

                    prediction = model.predict(images[i:i+1])
                    predicted_digit = np.argmax(prediction.asnumpy())
                    probabilities = softmax(prediction.asnumpy()[0])  # 使用softmax得到概率
                    # probabilities = prediction.asnumpy()[0]
                    predictions_dict[digit] = (predicted_digit, probabilities)

            if len(found_digits) == 10:
                break

        except StopIteration:
            data_iter = test_dataset.create_dict_iterator()

    # 创建一个 figure 和 GridSpec
    fig = plt.figure(figsize=(15, 8))
    gs = plt.GridSpec(2, 10, height_ratios=[1, 2])  # 2 行 10 列

    # 第一行：显示每个数字图像
    for i in range(10):
        ax = fig.add_subplot(gs[0, i])
        ax.imshow(images_dict[i].reshape(28, 28), cmap='gray')
        ax.set_title(f'数字: {i}', fontsize=10)
        ax.axis('off')

    # 第二行（合并所有列）：概率柱状图
    ax2 = fig.add_subplot(gs[1, :])
    ax2.set_title('模型预测概率分布')
    width = 0.08
    x = np.arange(10)

    for i in range(10):
        predicted_digit, probs = predictions_dict[i]
        offset = i * width
        ax2.bar(x + offset, probs, width, label=f'真实:{i}', alpha=0.7)

    ax2.set_xlabel('预测类别')
    ax2.set_ylabel('预测概率')
    ax2.set_xticks(x + width * 4.5)
    ax2.set_xticklabels(range(10))
    ax2.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=9)

    plt.tight_layout()
    plt.savefig('all_digits_prediction.png', dpi=300, bbox_inches='tight')
    print("\n所有数字的预测可视化已保存为 all_digits_prediction.png")



if __name__ == '__main__':
    # 设置运行设备
    ms.set_context(mode=ms.GRAPH_MODE, device_target="CPU")
    
    # 准备数据集目录
    data_dir = "./MNIST_Data"
    train_path = os.path.join(data_dir, "train")
    test_path = os.path.join(data_dir, "test")
    
    # 检查数据集是否存在，不存在则下载
    if not (os.path.exists(train_path) and os.path.exists(test_path)):
        print("未找到 MNIST 数据集，开始下载...")
        download_and_extract_mnist(data_dir)
    
    # 解压和组织数据集
    if not (os.path.exists(train_path) and os.path.exists(test_path)):
        print("准备数据集...")
        prepare_mnist_data(data_dir)

    # 创建训练集和测试集
    print("加载数据集...")
    train_dataset = create_dataset(train_path)
    test_dataset = create_dataset(test_path)
    print("数据集加载完成！")
    
    # 训练模型
    print("开始训练...")
    model = train_model(train_dataset, test_dataset, epochs=10)
    
    # 评估模型
    print("\n最终评估...")
    metrics = model.eval(test_dataset)
    print(f"测试集准确率: {metrics['accuracy']:.4f}")

    # 可视化所有数字的预测结果
    print("\n生成所有数字的预测可视化...")
    visualize_all_digits(model, test_dataset)
    
    # 保存模型
    ms.save_checkpoint(model._network, "lenet5.ckpt")
    print("模型已保存为 lenet5.ckpt")


