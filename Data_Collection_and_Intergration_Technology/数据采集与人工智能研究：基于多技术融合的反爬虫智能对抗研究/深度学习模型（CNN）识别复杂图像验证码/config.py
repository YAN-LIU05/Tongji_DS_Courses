"""
优化的配置文件
"""
import torch

# 数据路径
DATA_DIR = './data'
RAW_DATA_DIR = './data/raw'
TRAIN_DIR = './data/train'
VAL_DIR = './data/val'
TEST_DIR = './data/test'

# 模型保存路径
CHECKPOINT_DIR = './checkpoints'
RESULTS_DIR = './results'

# 数据集设置
IMAGE_WIDTH = 160
IMAGE_HEIGHT = 60
NUM_CHARS = 5
CHARSET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

# ✅ 优化的训练超参数
BATCH_SIZE = 128  # 更大的batch size
NUM_EPOCHS = 80  # 更多epoch
LEARNING_RATE = 0.001  # 初始学习率
NUM_WORKERS = 0

# 数据划分
TRAIN_RATIO = 0.7
VAL_RATIO = 0.15
TEST_RATIO = 0.15

# 设备
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')