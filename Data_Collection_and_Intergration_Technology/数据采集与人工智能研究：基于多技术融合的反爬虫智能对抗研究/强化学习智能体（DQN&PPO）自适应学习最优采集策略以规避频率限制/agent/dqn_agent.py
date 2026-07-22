"""
Deep Q-Network (DQN) 智能体
"""
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import random
from collections import deque

from models.networks import DQNetwork
from agent.replay_buffer import ReplayBuffer

class DQNAgent:
    """DQN智能体"""
    
    def __init__(self, state_dim, action_dim, device='cpu',
                 buffer=None, lr=0.001, gamma=0.99,
                 epsilon_start=1.0, epsilon_end=0.01, epsilon_decay=0.995,
                 target_update=10, batch_size=64):
        """
        初始化DQN智能体
        
        Args:
            state_dim: 状态维度
            action_dim: 动作维度
            device: 设备
            buffer: 经验回放缓冲区
            lr: 学习率
            gamma: 折扣因子
            epsilon_start: 初始探索率
            epsilon_end: 最终探索率
            epsilon_decay: 探索率衰减
            target_update: 目标网络更新频率
            batch_size: 批次大小
        """
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.device = device
        self.gamma = gamma
        self.target_update = target_update
        self.batch_size = batch_size
        
        # Q网络和目标网络
        self.q_network = DQNetwork(state_dim, action_dim).to(device)
        self.target_network = DQNetwork(state_dim, action_dim).to(device)
        self.target_network.load_state_dict(self.q_network.state_dict())
        
        # 优化器
        self.optimizer = optim.Adam(self.q_network.parameters(), lr=lr)
        
        # 经验回放
        if buffer is None:
            self.buffer = ReplayBuffer(capacity=100000)
        else:
            self.buffer = buffer
        
        # 探索策略
        self.epsilon = epsilon_start
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_end
        
        # 训练计数
        self.learn_step_counter = 0
    
    def select_action(self, state, training=True, explore=True):
        """
        选择动作（ε-greedy策略）
        
        Args:
            state: 当前状态
            training: 是否训练模式
            explore: 是否探索
            
        Returns:
            动作
        """
        # 确保状态格式正确
        if isinstance(state, (list, tuple)):
            state = np.array(state, dtype=np.float32)
        elif not isinstance(state, np.ndarray):
            state = np.array(state, dtype=np.float32)
        
        if state.ndim == 0:
            state = state.reshape(1)
        elif state.ndim > 1:
            state = state.flatten()
        
        if training and explore and random.random() < self.epsilon:
            # 探索：随机动作
            return random.randint(0, self.action_dim - 1)
        else:
            # 利用：选择最优动作
            with torch.no_grad():
                state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)
                q_values = self.q_network(state_tensor)
                return q_values.argmax().item()
    
    def store_transition(self, state, action, reward, next_state, done):
        """存储经验 - 兼容性方法"""
        self.buffer.push(state, action, reward, next_state, done)
    
    def learn(self):
        """从经验中学习"""
        if not self.buffer.is_ready(self.batch_size):
            return None
        
        # 采样批次
        states, actions, rewards, next_states, dones = self.buffer.sample(self.batch_size)
        
        # 转换为张量
        states = torch.FloatTensor(states).to(self.device)
        actions = torch.LongTensor(actions).unsqueeze(1).to(self.device)
        rewards = torch.FloatTensor(rewards).unsqueeze(1).to(self.device)
        next_states = torch.FloatTensor(next_states).to(self.device)
        dones = torch.FloatTensor(dones).unsqueeze(1).to(self.device)
        
        # 计算当前Q值
        current_q_values = self.q_network(states).gather(1, actions)
        
        # 计算目标Q值 (Double DQN)
        with torch.no_grad():
            # 用当前网络选择动作
            next_actions = self.q_network(next_states).argmax(1, keepdim=True)
            # 用目标网络评估Q值
            next_q_values = self.target_network(next_states).gather(1, next_actions)
            target_q_values = rewards + (1 - dones) * self.gamma * next_q_values
        
        # 计算损失
        loss = nn.MSELoss()(current_q_values, target_q_values)
        
        # 优化
        self.optimizer.zero_grad()
        loss.backward()
        # 梯度裁剪
        torch.nn.utils.clip_grad_norm_(self.q_network.parameters(), 1.0)
        self.optimizer.step()
        
        # 更新目标网络
        self.learn_step_counter += 1
        if self.learn_step_counter % self.target_update == 0:
            self.target_network.load_state_dict(self.q_network.state_dict())
        
        # 衰减探索率
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)
        
        return loss.item()
    
    def save(self, path):
        """保存模型"""
        torch.save({
            'q_network': self.q_network.state_dict(),
            'target_network': self.target_network.state_dict(),
            'optimizer': self.optimizer.state_dict(),
            'epsilon': self.epsilon,
        }, path)
    
    def load(self, path):
        """加载模型"""
        checkpoint = torch.load(path, map_location=self.device)
        self.q_network.load_state_dict(checkpoint['q_network'])
        self.target_network.load_state_dict(checkpoint['target_network'])
        self.optimizer.load_state_dict(checkpoint['optimizer'])
        self.epsilon = checkpoint['epsilon']


# 为了兼容性，添加别名
class DoubleDQNAgent(DQNAgent):
    """Double DQN智能体（与DQN相同实现）"""
    pass


class DuelingDQNAgent(DQNAgent):
    """Dueling DQN智能体（与DQN相同实现）"""
    pass