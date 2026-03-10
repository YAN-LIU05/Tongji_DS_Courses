"""
强化学习训练主程序
"""
import os
import sys
import numpy as np
import torch
from tqdm import tqdm
import matplotlib.pyplot as plt
from datetime import datetime

from config.config import Config
from environment.anti_spider_env import AntiSpiderEnvironment
from agent.dqn_agent import DQNAgent
from agent.ppo_agent import PPOAgent
from utils.logger import Logger
from utils.visualizer import Visualizer
import argparse

class RLTrainer:
    """强化学习训练器"""
    
    def __init__(self, agent_type='dqn', use_realistic_env=True):
        """初始化训练器"""
        self.agent_type = agent_type.lower()
        self.use_realistic_env = use_realistic_env
        
        # 环境配置
        self.config = {
            'ip_pool_size': 50,
            'max_requests': 1000,
            'ua_pool_size': 20,
            'detection_threshold': 0.7,
            'ban_penalty': -10,
            'success_reward': 1
        }
        
        # 创建环境
        if use_realistic_env:
            from environment.anti_spider_env import RealisticAntiSpiderEnvironment, HellModeAntiSpiderEnvironment
            self.env = RealisticAntiSpiderEnvironment(self.config)
            print("使用真实反爬虫环境")
        else:
            from environment.anti_spider_env import AntiSpiderEnvironment
            self.env = AntiSpiderEnvironment(self.config)
            print("使用简单反爬虫环境")
        

        # 🔧 正确获取环境的状态和动作维度
        self.state_dim = self.env.observation_space.shape[0]
        self.action_dim = self.env.action_space.n
        
        # 设备配置
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # 创建智能体
        self.agent = self.create_agent()
        
        # 训练配置
        self.episodes = 1000
        self.max_steps = 1000
        self.save_interval = 50
        self.log_interval = 10
        
        # 创建保存目录
        self.model_dir = 'models'
        self.log_dir = 'logs'
        os.makedirs(self.model_dir, exist_ok=True)
        os.makedirs(self.log_dir, exist_ok=True)
        
        # 训练统计
        self.stats = {
            'episode_rewards': [],
            'episode_steps': [],
            'success_rates': [],
            'losses': []
        }
        
        print("=" * 70)
        print("强化学习训练器初始化完成")
        print(f"智能体类型: {self.agent_type.upper()}")
        print(f"状态维度: {self.state_dim}")
        print(f"动作空间: {self.action_dim}")
        print(f"设备: {self.device}")
        print("=" * 70)
    
    def create_agent(self):
        """创建智能体"""
        if self.agent_type == 'dqn':
            from agent.dqn_agent import DQNAgent
            return DQNAgent(
                state_dim=self.state_dim,
                action_dim=self.action_dim,
                device=self.device
            )
        elif self.agent_type == 'ddqn':
            from agent.ddqn_agent import DoubleDQNAgent
            return DoubleDQNAgent(
                state_dim=self.state_dim,
                action_dim=self.action_dim,
                device=self.device
            )
        elif self.agent_type == 'ppo':
            from agent.ppo_agent import PPOAgent
            return PPOAgent(
                state_dim=self.state_dim,
                action_dim=self.action_dim,
                device=self.device
            )
        else:
            raise ValueError(f"未知的智能体类型: {self.agent_type}")
    
    def train(self):
        """训练智能体"""
        print(f"\n开始训练 {self.episodes} 个回合...\n")
        
        for episode in range(self.episodes):
            episode_stats = self.train_episode(episode)
            
            # 记录统计信息
            self.stats['episode_rewards'].append(episode_stats['reward'])
            self.stats['episode_steps'].append(episode_stats['steps'])
            self.stats['success_rates'].append(episode_stats['success_rate'])
            
            # 定期打印信息
            if (episode + 1) % self.log_interval == 0:
                avg_reward = np.mean(self.stats['episode_rewards'][-self.log_interval:])
                avg_steps = np.mean(self.stats['episode_steps'][-self.log_interval:])
                avg_success = np.mean(self.stats['success_rates'][-self.log_interval:])
                
                print(f"回合 {episode + 1}/{self.episodes}")
                print(f"  平均奖励: {avg_reward:.2f}")
                print(f"  平均步数: {avg_steps:.0f}")
                print(f"  平均成功率: {avg_success:.2%}")
                print(f"  Epsilon: {self.agent.epsilon if hasattr(self.agent, 'epsilon') else 'N/A'}")
                print("-" * 70)
            
            # 定期保存模型
            if (episode + 1) % self.save_interval == 0:
                self.save_checkpoint(episode + 1)
        
        # 训练结束后保存最终模型
        self.save_checkpoint('final')
        self.plot_training_stats()
        
        print("\n训练完成！")
    
    def train_episode(self, episode):
        """
        训练单个回合
        
        Args:
            episode: 回合编号
            
        Returns:
            回合统计信息
        """
        # 🔧 正确解包 reset 返回值
        state, info = self.env.reset()
        
        # 🔧 确保 state 是 numpy 数组
        if not isinstance(state, np.ndarray):
            state = np.array(state, dtype=np.float32)
        
        episode_reward = 0
        episode_steps = 0
        
        # 调试信息（仅第一个回合）
        if episode == 0:
            print(f"\n{'='*60}")
            print(f"[调试信息]")
            print(f"状态类型: {type(state)}")
            print(f"状态形状: {state.shape}")
            print(f"状态内容: {state}")
            print(f"期望维度: {self.state_dim}")
            print(f"动作空间: {self.action_dim}")
            print(f"{'='*60}\n")
        
        done = False
        
        while not done:
            # 选择动作
            if self.agent_type == 'ppo':
                action, log_prob, value = self.agent.select_action(state, training=True)
                
                # 执行动作
                next_state, reward, terminated, truncated, info = self.env.step(action)
                done = terminated or truncated
                
                # 🔧 确保 next_state 是 numpy 数组
                if not isinstance(next_state, np.ndarray):
                    next_state = np.array(next_state, dtype=np.float32)
                
                # 存储经验
                self.agent.memory.push(state, action, reward, next_state, done, log_prob, value)
                
            else:  # DQN类智能体
                action = self.agent.select_action(state)
                
                # 执行动作
                next_state, reward, terminated, truncated, info = self.env.step(action)
                done = terminated or truncated
                
                # 🔧 确保 next_state 是 numpy 数组
                if not isinstance(next_state, np.ndarray):
                    next_state = np.array(next_state, dtype=np.float32)
                
                self.agent.buffer.push(state, action, reward, next_state, done)
            
            state = next_state
            episode_reward += reward
            episode_steps += 1
            
            # 学习
            if self.agent_type == 'ppo':
                if episode_steps % self.agent.update_freq == 0:
                    self.agent.update()
            else:
                if self.agent.buffer.is_ready(self.agent.batch_size):
                    loss = self.agent.learn()
                    if loss is not None:
                        self.stats['losses'].append(loss)
        
        # PPO在回合结束时更新
        if self.agent_type == 'ppo':
            self.agent.update()
        
        return {
            'reward': episode_reward,
            'steps': episode_steps,
            'success_rate': info.get('success_count', 0) / max(1, info.get('request_count', 1))
        }
    
    def evaluate(self, num_episodes=10):
        """
        评估智能体性能
        
        Args:
            num_episodes: 评估回合数
        """
        print(f"\n开始评估 {num_episodes} 个回合...")
        
        eval_rewards = []
        eval_success_rates = []
        
        for episode in range(num_episodes):
            state, _ = self.env.reset()
            episode_reward = 0
            done = False
            
            while not done:
                if self.agent_type == 'ppo':
                    action = self.agent.select_action(state, training=False)
                else:
                    # DQN评估时不使用epsilon探索
                    old_epsilon = self.agent.epsilon
                    self.agent.epsilon = 0
                    action = self.agent.select_action(state)
                    self.agent.epsilon = old_epsilon
                
                next_state, reward, terminated, truncated, info = self.env.step(action)
                done = terminated or truncated
                
                state = next_state
                episode_reward += reward
            
            eval_rewards.append(episode_reward)
            success_rate = info.get('success_count', 0) / max(1, info.get('request_count', 1))
            eval_success_rates.append(success_rate)
            
            print(f"评估回合 {episode + 1}: 奖励={episode_reward:.2f}, 成功率={success_rate:.2%}")
        
        print(f"\n评估结果:")
        print(f"  平均奖励: {np.mean(eval_rewards):.2f} ± {np.std(eval_rewards):.2f}")
        print(f"  平均成功率: {np.mean(eval_success_rates):.2%} ± {np.std(eval_success_rates):.2%}")
    
    def save_checkpoint(self, episode):
        """保存检查点"""
        checkpoint = {
            'episode': episode,
            'agent_type': self.agent_type,
            'state_dim': self.state_dim,
            'action_dim': self.action_dim,
            'stats': self.stats
        }
        
        # 保存智能体
        if self.agent_type == 'ppo':
            checkpoint['actor_state_dict'] = self.agent.actor.state_dict()
            checkpoint['critic_state_dict'] = self.agent.critic.state_dict()
            checkpoint['actor_optimizer'] = self.agent.actor_optimizer.state_dict()
            checkpoint['critic_optimizer'] = self.agent.critic_optimizer.state_dict()
        else:
            checkpoint['model_state_dict'] = self.agent.q_network.state_dict()
            checkpoint['optimizer'] = self.agent.optimizer.state_dict()
            checkpoint['epsilon'] = self.agent.epsilon
        
        save_path = os.path.join(self.model_dir, f'{self.agent_type}_checkpoint_{episode}.pth')
        torch.save(checkpoint, save_path)
        print(f"检查点已保存: {save_path}")
    
    def load_checkpoint(self, checkpoint_path):
        """加载检查点"""
        checkpoint = torch.load(checkpoint_path, map_location=self.device)
        
        if self.agent_type == 'ppo':
            self.agent.actor.load_state_dict(checkpoint['actor_state_dict'])
            self.agent.critic.load_state_dict(checkpoint['critic_state_dict'])
            self.agent.actor_optimizer.load_state_dict(checkpoint['actor_optimizer'])
            self.agent.critic_optimizer.load_state_dict(checkpoint['critic_optimizer'])
        else:
            self.agent.q_network.load_state_dict(checkpoint['model_state_dict'])
            self.agent.optimizer.load_state_dict(checkpoint['optimizer'])
            self.agent.epsilon = checkpoint['epsilon']
        
        self.stats = checkpoint['stats']
        print(f"检查点已加载: {checkpoint_path}")
        print(f"回合: {checkpoint['episode']}")
    
    def plot_training_stats(self):
        """绘制训练统计图"""
        import matplotlib.pyplot as plt
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # 回合奖励
        axes[0, 0].plot(self.stats['episode_rewards'])
        axes[0, 0].set_title('Episode Rewards')
        axes[0, 0].set_xlabel('Episode')
        axes[0, 0].set_ylabel('Reward')
        axes[0, 0].grid(True)
        
        # 回合步数
        axes[0, 1].plot(self.stats['episode_steps'])
        axes[0, 1].set_title('Episode Steps')
        axes[0, 1].set_xlabel('Episode')
        axes[0, 1].set_ylabel('Steps')
        axes[0, 1].grid(True)
        
        # 成功率
        axes[1, 0].plot(self.stats['success_rates'])
        axes[1, 0].set_title('Success Rate')
        axes[1, 0].set_xlabel('Episode')
        axes[1, 0].set_ylabel('Success Rate')
        axes[1, 0].grid(True)
        
        # 损失（如果有）
        if self.stats['losses']:
            axes[1, 1].plot(self.stats['losses'])
            axes[1, 1].set_title('Training Loss')
            axes[1, 1].set_xlabel('Update Step')
            axes[1, 1].set_ylabel('Loss')
            axes[1, 1].grid(True)
        
        plt.tight_layout()
        plot_path = os.path.join(self.log_dir, f'{self.agent_type}_training_stats.png')
        plt.savefig(plot_path)
        print(f"训练统计图已保存: {plot_path}")
        plt.close()


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='强化学习反爬虫训练')
    parser.add_argument('--agent', type=str, default='ppo',
                        choices=['dqn', 'ddqn', 'ppo'],
                        help='智能体类型')
    parser.add_argument('--episodes', type=int, default=1000,
                        help='训练回合数')
    parser.add_argument('--eval', action='store_true',
                        help='评估模式')
    parser.add_argument('--load', type=str, default=None,
                        help='加载检查点路径')
    
    args = parser.parse_args()
    
    # 创建训练器
    trainer = RLTrainer(agent_type=args.agent)
    trainer.episodes = args.episodes
    
    # 加载检查点（如果指定）
    if args.load:
        trainer.load_checkpoint(args.load)
    
    # 训练或评估
    if args.eval:
        trainer.evaluate()
    else:
        trainer.train()


if __name__ == '__main__':
    main()


