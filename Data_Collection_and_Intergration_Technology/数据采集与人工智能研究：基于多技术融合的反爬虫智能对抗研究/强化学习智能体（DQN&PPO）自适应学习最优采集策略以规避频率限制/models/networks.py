"""
神经网络架构
"""
import torch
import torch.nn as nn
import torch.nn.functional as F

class DQNetwork(nn.Module):
    """DQN的Q网络"""
    
    def __init__(self, state_dim, action_dim, hidden_dim=256):
        super(DQNetwork, self).__init__()
        
        # Dueling DQN架构
        self.feature = nn.Sequential(
            nn.Linear(state_dim, hidden_dim),
            nn.ReLU(),
            nn.LayerNorm(hidden_dim),
            nn.Dropout(0.2),
            
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.LayerNorm(hidden_dim),
            nn.Dropout(0.2),
        )
        
        # 价值流
        self.value_stream = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Linear(hidden_dim // 2, 1)
        )
        
        # 优势流
        self.advantage_stream = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Linear(hidden_dim // 2, action_dim)
        )
    
    def forward(self, state):
        features = self.feature(state)
        value = self.value_stream(features)
        advantage = self.advantage_stream(features)
        
        # Q = V + (A - mean(A))
        q_values = value + (advantage - advantage.mean(dim=1, keepdim=True))
        return q_values


class ActorCriticNetwork(nn.Module):
    """PPO的Actor-Critic网络"""
    
    def __init__(self, state_dim, action_dim, hidden_dim=256):
        super(ActorCriticNetwork, self).__init__()
        
        # 共享特征提取
        self.shared = nn.Sequential(
            nn.Linear(state_dim, hidden_dim),
            nn.ReLU(),
            nn.LayerNorm(hidden_dim),
            
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.LayerNorm(hidden_dim),
        )
        
        # Actor (策略网络)
        self.actor = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Linear(hidden_dim // 2, action_dim),
            nn.Softmax(dim=-1)
        )
        
        # Critic (价值网络)
        self.critic = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Linear(hidden_dim // 2, 1)
        )
    
    def forward(self, state):
        features = self.shared(state)
        action_probs = self.actor(features)
        state_value = self.critic(features)
        return action_probs, state_value
    
    def get_action(self, state):
        """采样动作"""
        action_probs, _ = self.forward(state)
        dist = torch.distributions.Categorical(action_probs)
        action = dist.sample()
        return action, dist.log_prob(action), dist.entropy()
    
    def evaluate_actions(self, states, actions):
        """评估动作"""
        action_probs, state_values = self.forward(states)
        dist = torch.distributions.Categorical(action_probs)
        action_log_probs = dist.log_prob(actions)
        entropy = dist.entropy()
        return action_log_probs, state_values, entropy