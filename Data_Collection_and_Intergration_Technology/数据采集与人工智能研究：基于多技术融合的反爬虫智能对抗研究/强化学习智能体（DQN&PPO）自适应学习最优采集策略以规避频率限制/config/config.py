"""
强化学习配置
"""
import torch

class Config:
    # ==================== 环境配置 ====================
    # 状态空间维度
    STATE_DIM = 12  # [当前间隔, 成功率, 失败次数, 时段, IP复用次数, 上次请求时间差, 
                    #  连续成功次数, 连续失败次数, 累计请求数, 当前IP年龄, 
                    #  当前User-Agent年龄, 风险评分]
    
    # 动作空间（离散动作）
    ACTION_DIM = 9
    ACTIONS = {
        0: {'interval': 0.5, 'change_ip': False, 'change_ua': False},   # 快速请求
        1: {'interval': 1.0, 'change_ip': False, 'change_ua': False},   # 正常请求
        2: {'interval': 2.0, 'change_ip': False, 'change_ua': False},   # 慢速请求
        3: {'interval': 1.0, 'change_ip': True, 'change_ua': False},    # 换IP
        4: {'interval': 1.0, 'change_ip': False, 'change_ua': True},    # 换UA
        5: {'interval': 1.0, 'change_ip': True, 'change_ua': True},     # 全换
        6: {'interval': 3.0, 'change_ip': False, 'change_ua': False},   # 等待冷却
        7: {'interval': 5.0, 'change_ip': True, 'change_ua': False},    # 长等待+换IP
        8: {'interval': 10.0, 'change_ip': True, 'change_ua': True},    # 紧急避险
    }
    
    # 奖励设置
    REWARD_SUCCESS = 1.0           # 成功请求的奖励
    REWARD_BLOCK = -5.0            # 被封禁的惩罚
    REWARD_CAPTCHA = -2.0          # 遇到验证码的惩罚
    REWARD_TIMEOUT = -1.0          # 超时的惩罚
    REWARD_EFFICIENCY = 0.1        # 效率奖励（快速成功）
    REWARD_IP_CHANGE = -0.1        # 换IP的小惩罚（成本）
    
    # 反爬虫策略模拟参数
    BLOCK_THRESHOLD = 10           # 短时间内请求次数阈值
    BLOCK_TIME_WINDOW = 10         # 检测时间窗口（秒）
    IP_BAN_DURATION = 300          # IP封禁时长（秒）
    CAPTCHA_PROBABILITY = 0.1      # 触发验证码概率
    
    # ==================== DQN配置 ====================
    GAMMA = 0.99                   # 折扣因子
    EPSILON_START = 1.0            # 初始探索率
    EPSILON_END = 0.05             # 最终探索率
    EPSILON_DECAY = 0.995          # 探索率衰减
    
    BATCH_SIZE = 128               # 批次大小
    BUFFER_SIZE = 100000           # 经验回放缓冲区大小
    LEARNING_RATE = 0.001          # 学习率
    TARGET_UPDATE = 10             # 目标网络更新频率
    
    # ==================== PPO配置 ====================
    PPO_EPOCHS = 4                 # PPO更新轮数
    PPO_CLIP = 0.2                 # PPO裁剪参数
    PPO_LR = 3e-4                  # PPO学习率
    VALUE_COEF = 0.5               # 价值损失系数
    ENTROPY_COEF = 0.05            # 熵正则化系数
    
    # ==================== 训练配置 ====================
    NUM_EPISODES = 100             # 训练回合数
    MAX_STEPS_PER_EPISODE = 50     # 每回合最大步数
    EVAL_FREQUENCY = 50            # 评估频率
    SAVE_FREQUENCY = 10           # 保存频率
    
    # 设备
    DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    # 路径
    CHECKPOINT_DIR = './checkpoints'
    LOG_DIR = './logs'
    RESULTS_DIR = './results'