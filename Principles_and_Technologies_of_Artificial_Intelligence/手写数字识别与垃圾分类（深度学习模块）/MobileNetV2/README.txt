这个是MobileNetV2的模型代码和数据集，本实验使用python3.10
文件夹结构如下：

├── MobileNetV2
  ├── README.md     # descriptions about MobileNetV2
  ├── scripts
  │   ├──run_train.sh   # shell script for train, fine_tune or incremental  learn with CPU, GPU or Ascend
  │   ├──run_eval.sh    # shell script for evaluation with CPU, GPU or Ascend
  │   ├──run_train_tiny.sh
  │   ├──run_eval_tiny.sh
  │   ├──run_train_tiny.bat
  │   ├──run_eval_tiny.bat
  ├── src
  │   ├──args.py        # parse args
  │   ├──config.py      # parameter configuration
  │   ├──dataset.py     # creating dataset
  │   ├──launch.py      # start python script
  │   ├──lr_generator.py     # learning rate config
  │   ├──mobilenetV2.py      # MobileNetV2 architecture
  │   ├──models.py      # contain define_net and Loss, Monitor
  │   ├──utils.py       # utils to load ckpt_file for fine tune or incremental learn
  ├── train.py      # training script
  ├── eval.py       # evaluation script
  ├── mindspore_hub_conf.py       #  mindspore hub interface
├── data
  ├── train 
  ├── test
├── data_new
  ├── test
├── pretrain_checkpoint
  ├── mobilenetv2_cpu_gpu.ckpt
├── deal_dataset.py
├── requirements.txt
├── README.txt

其中需要说明的是，run_train_tiny.sh和run_eval_tiny.sh是专门为这次实验编写的时候快速开始实验的bash文件，仅用于CPU微调。
data是训练用数据集，data_new/test是data/test经deal_dataset.py处理后的验证集，加了变换和噪声。
实验方法如下：
1.训练微调模型：
bash code/scripts/run_train_tiny.sh
2.测试模型
bash code/scripts/run_test_tiny.sh
在Windows系统可以使用bat文件代替。