"""
Proximal Policy Optimization (PPO) 智能体
相比DQN更稳定，更适合连续决策任务
"""
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from collections import deque

from models.networks import ActorCriticNetwork

class PPOMemory:
    """PPO经验存储"""
    
    def __init__(self):
        self.states = []
        self.actions = []
        self.rewards = []
        self.log_probs = []
        self.values = []
        self.dones = []
    
    def push(self, state, action, reward, next_state, done, log_prob, value):
        """存储经验"""
        self.states.append(state)
        self.actions.append(action)
        self.rewards.append(reward)
        self.log_probs.append(log_prob)
        self.values.append(value)
        self.dones.append(done)
    
    def clear(self):
        """清空记忆"""
        self.states = []
        self.actions = []
        self.rewards = []
        self.log_probs = []
        self.values = []
        self.dones = []
    
    def __len__(self):
        return len(self.states)


class PPOAgent:
    """PPO智能体 - 更稳定的策略梯度方法"""
    
    def __init__(self, state_dim, action_dim, device='cpu', 
                 lr=3e-4, gamma=0.99, gae_lambda=0.95,
                 clip_epsilon=0.2, value_coef=0.5, entropy_coef=0.01,
                 update_freq=2048, epochs=10, batch_size=64):
        """
        初始化PPO智能体
        
        Args:
            state_dim: 状态维度
            action_dim: 动作维度
            device: 设备
            lr: 学习率
            gamma: 折扣因子
            gae_lambda: GAE lambda参数
            clip_epsilon: PPO裁剪参数
            value_coef: 价值损失系数
            entropy_coef: 熵系数
            update_freq: 更新频率
            epochs: PPO更新轮数
            batch_size: 批次大小
        """
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.device = device
        self.gamma = gamma
        self.gae_lambda = gae_lambda
        self.clip_epsilon = clip_epsilon
        self.value_coef = value_coef
        self.entropy_coef = entropy_coef
        self.update_freq = update_freq
        self.epochs = epochs
        self.batch_size = batch_size
        
        # 创建Actor-Critic网络
        self.policy = ActorCriticNetwork(state_dim, action_dim).to(device)
        self.optimizer = optim.Adam(self.policy.parameters(), lr=lr)
        
        # 为了兼容性，添加actor和critic别名
        self.actor = self.policy
        self.critic = self.policy
        
        # 创建优化器别名
        self.actor_optimizer = self.optimizer
        self.critic_optimizer = self.optimizer
        
        # 经验存储
        self.memory = PPOMemory()
        
        # 训练统计
        self.epsilon = 0  # 占位符，PPO不使用epsilon
    
    def select_action(self, state, training=True):
        """
        选择动作
        
        Args:
            state: 当前状态
            training: 是否处于训练模式
            
        Returns:
            训练模式: (action, log_prob, value)
            评估模式: action
        """
        # 确保状态格式正确
        if isinstance(state, (list, tuple)):
            state = np.array(state, dtype=np.float32)
        elif not isinstance(state, np.ndarray):
            state = np.array(state, dtype=np.float32)
        
        # 确保是1维数组
        if state.ndim == 0:
            state = state.reshape(1)
        elif state.ndim > 1:
            state = state.flatten()
        
        # 转换为tensor
        state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)
        
        with torch.no_grad():
            action_probs, value = self.policy(state_tensor)
            
            if training:
                # 训练模式：从分布中采样
                dist = torch.distributions.Categorical(action_probs)
                action = dist.sample()
                log_prob = dist.log_prob(action)
                
                return action.item(), log_prob.item(), value.item()
            else:
                # 评估模式：选择概率最高的动作
                action = torch.argmax(action_probs, dim=1)
                return action.item()
    
    def compute_returns_and_advantages(self, next_state):
        """计算回报和优势函数 (GAE)"""
        if len(self.memory) == 0:
            return [], []
        
        # 计算最后一个值
        with torch.no_grad():
            if isinstance(next_state, (list, tuple)):
                next_state = np.array(next_state, dtype=np.float32)
            
            next_state_tensor = torch.FloatTensor(next_state).unsqueeze(0).to(self.device)
            _, next_value = self.policy(next_state_tensor)
            next_value = next_value.item()
        
        returns = []
        advantages = []
        values = self.memory.values + [next_value]
        
        gae = 0
        for step in reversed(range(len(self.memory.rewards))):
            # TD误差
            delta = (self.memory.rewards[step] + 
                    self.gamma * values[step + 1] * (1 - self.memory.dones[step]) - 
                    values[step])
            
            # GAE
            gae = delta + self.gamma * self.gae_lambda * (1 - self.memory.dones[step]) * gae
            
            advantages.insert(0, gae)
            returns.insert(0, gae + values[step])
        
        return returns, advantages
    
    def update(self):
        """PPO更新"""
        if len(self.memory) == 0:
            return None
        
        # 计算回报和优势 - 使用最后一个状态
        if len(self.memory.states) > 0:
            next_state = self.memory.states[-1]  # 使用最后一个状态作为近似
        else:
            return None
        
        returns, advantages = self.compute_returns_and_advantages(next_state)
        
        if len(returns) == 0:
            return None
        
        # 转换为张量
        states = torch.FloatTensor(np.array(self.memory.states)).to(self.device)
        actions = torch.LongTensor(self.memory.actions).to(self.device)
        old_log_probs = torch.FloatTensor(self.memory.log_probs).to(self.device)
        returns_tensor = torch.FloatTensor(returns).to(self.device)
        advantages_tensor = torch.FloatTensor(advantages).to(self.device)
        
        # 标准化优势
        advantages_tensor = (advantages_tensor - advantages_tensor.mean()) / (advantages_tensor.std() + 1e-8)
        
        # PPO更新多个epoch
        total_policy_loss = 0
        total_value_loss = 0
        total_entropy = 0
        
        for _ in range(self.epochs):
            # 重新评估动作
            new_log_probs, state_values, entropy = self.policy.evaluate_actions(states, actions)
            
            # 计算比率
            ratio = torch.exp(new_log_probs - old_log_probs)
            
            # Clipped surrogate loss
            surr1 = ratio * advantages_tensor
            surr2 = torch.clamp(ratio, 1.0 - self.clip_epsilon, 
                               1.0 + self.clip_epsilon) * advantages_tensor
            policy_loss = -torch.min(surr1, surr2).mean()
            
            # Value loss
            value_loss = nn.MSELoss()(state_values.squeeze(), returns_tensor)
            
            # 总损失
            loss = (policy_loss + 
                   self.value_coef * value_loss - 
                   self.entropy_coef * entropy.mean())
            
            # 优化
            self.optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(self.policy.parameters(), 0.5)
            self.optimizer.step()
            
            total_policy_loss += policy_loss.item()
            total_value_loss += value_loss.item()
            total_entropy += entropy.mean().item()
        
        # 清空缓冲区
        self.memory.clear()
        
        return {
            'policy_loss': total_policy_loss / self.epochs,
            'value_loss': total_value_loss / self.epochs,
            'entropy': total_entropy / self.epochs
        }
    
    def save(self, path):
        """保存模型"""
        torch.save({
            'policy': self.policy.state_dict(),
            'optimizer': self.optimizer.state_dict(),
        }, path)
    
    def load(self, path):
        """加载模型"""
        checkpoint = torch.load(path, map_location=self.device)
        self.policy.load_state_dict(checkpoint['policy'])
        self.optimizer.load_state_dict(checkpoint['optimizer'])