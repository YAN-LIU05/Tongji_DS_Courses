"""
评估脚本 - evaluate.py
系统性评估训练好的DQN智能体性能
包括多指标评估、统计分析、可视化等功能
"""
import gymnasium as gym
import numpy as np
import torch
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import json
from datetime import datetime
import argparse
from typing import Dict, List, Tuple

from agent.dqn_agent import DQNAgent, DoubleDQNAgent, DuelingDQNAgent
from agent.replay_buffer import ReplayBuffer, PrioritizedReplayBuffer, NStepReplayBuffer


class Evaluator:
    """智能体评估器"""
    
    def __init__(self, env_name: str = 'CartPole-v1'):
        """
        初始化评估器
        
        Args:
            env_name: 环境名称
        """
        self.env_name = env_name
        self.env = gym.make(env_name)
        self.state_dim = self.env.observation_space.shape[0]
        self.action_dim = self.env.action_space.n
        
        # 评估结果存储
        self.results = {
            'episode_rewards': [],
            'episode_lengths': [],
            'success_rate': 0.0,
            'avg_reward': 0.0,
            'std_reward': 0.0,
            'min_reward': 0.0,
            'max_reward': 0.0,
            'median_reward': 0.0
        }
    
    def create_agent(self, agent_type: str, buffer_type: str) -> Tuple:
        """
        创建智能体和缓冲区
        
        Args:
            agent_type: 智能体类型
            buffer_type: 缓冲区类型
            
        Returns:
            (agent, buffer)
        """
        # 创建缓冲区
        if buffer_type == 'replay':
            buffer = ReplayBuffer(capacity=10000)
        elif buffer_type == 'prioritized':
            buffer = PrioritizedReplayBuffer(capacity=10000, alpha=0.6)
        elif buffer_type == 'nstep':
            buffer = NStepReplayBuffer(capacity=10000, n_step=3, gamma=0.99)
        else:
            raise ValueError(f"未知的缓冲区类型: {buffer_type}")
        
        # 创建智能体
        agent_params = {
            'state_dim': self.state_dim,
            'action_dim': self.action_dim,
            'buffer': buffer,
            'lr': 1e-3,
            'gamma': 0.99,
            'epsilon_start': 0.0,  # 评估时不探索
            'epsilon_end': 0.0,
            'epsilon_decay': 1.0
        }
        
        if agent_type == 'dqn':
            agent = DQNAgent(**agent_params)
        elif agent_type == 'double_dqn':
            agent = DoubleDQNAgent(**agent_params)
        elif agent_type == 'dueling_dqn':
            agent = DuelingDQNAgent(**agent_params)
        else:
            raise ValueError(f"未知的智能体类型: {agent_type}")
        
        return agent, buffer
    
    def evaluate_agent(self, agent, episodes: int = 100, 
                      render: bool = False, verbose: bool = True) -> Dict:
        """
        评估智能体
        
        Args:
            agent: 智能体
            episodes: 评估回合数
            render: 是否渲染
            verbose: 是否打印详细信息
            
        Returns:
            评估结果字典
        """
        episode_rewards = []
        episode_lengths = []
        success_count = 0
        
        if verbose:
            print(f"\n{'='*70}")
            print(f"开始评估 (共 {episodes} 回合)")
            print(f"{'='*70}\n")
        
        for episode in range(episodes):
            state, _ = self.env.reset()
            episode_reward = 0
            episode_length = 0
            done = False
            
            while not done:
                if render:
                    self.env.render()
                
                # 选择动作（贪婪策略）
                action = agent.select_action(state, explore=False)
                
                # 执行动作
                next_state, reward, terminated, truncated, _ = self.env.step(action)
                done = terminated or truncated
                
                episode_reward += reward
                episode_length += 1
                state = next_state
            
            episode_rewards.append(episode_reward)
            episode_lengths.append(episode_length)
            
            # 判断是否成功（针对CartPole，奖励>=475视为成功）
            if self.env_name == 'CartPole-v1' and episode_reward >= 475:
                success_count += 1
            
            if verbose and (episode + 1) % 10 == 0:
                print(f"回合 {episode + 1:3d}/{episodes}: "
                      f"平均奖励 = {np.mean(episode_rewards[-10:]):.2f}")
        
        # 计算统计指标
        self.results = {
            'episode_rewards': episode_rewards,
            'episode_lengths': episode_lengths,
            'success_rate': success_count / episodes * 100,
            'avg_reward': np.mean(episode_rewards),
            'std_reward': np.std(episode_rewards),
            'min_reward': np.min(episode_rewards),
            'max_reward': np.max(episode_rewards),
            'median_reward': np.median(episode_rewards),
            'avg_length': np.mean(episode_lengths),
            'total_episodes': episodes
        }
        
        if verbose:
            self.print_results()
        
        return self.results
    
    def print_results(self):
        """打印评估结果"""
        print(f"\n{'='*70}")
        print(f"评估结果")
        print(f"{'='*70}")
        print(f"总回合数:      {self.results['total_episodes']}")
        print(f"平均奖励:      {self.results['avg_reward']:.2f} ± {self.results['std_reward']:.2f}")
        print(f"中位数奖励:    {self.results['median_reward']:.2f}")
        print(f"最小奖励:      {self.results['min_reward']:.2f}")
        print(f"最大奖励:      {self.results['max_reward']:.2f}")
        print(f"平均步数:      {self.results['avg_length']:.2f}")
        print(f"成功率:        {self.results['success_rate']:.2f}%")
        print(f"{'='*70}\n")
    
    def plot_results(self, save_path: str = 'results/evaluation_results.png'):
        """
        绘制评估结果
        
        Args:
            save_path: 保存路径
        """
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        rewards = self.results['episode_rewards']
        lengths = self.results['episode_lengths']
        
        # 子图1: 奖励曲线
        axes[0, 0].plot(rewards, alpha=0.6, linewidth=1)
        axes[0, 0].plot(np.convolve(rewards, np.ones(10)/10, mode='valid'), 
                        color='red', linewidth=2, label='移动平均(10)')
        axes[0, 0].axhline(y=self.results['avg_reward'], color='green', 
                          linestyle='--', label=f"平均值 = {self.results['avg_reward']:.2f}")
        axes[0, 0].set_xlabel('回合', fontsize=12)
        axes[0, 0].set_ylabel('奖励', fontsize=12)
        axes[0, 0].set_title('回合奖励曲线', fontsize=14, fontweight='bold')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)
        
        # 子图2: 奖励分布
        axes[0, 1].hist(rewards, bins=30, edgecolor='black', alpha=0.7, color='skyblue')
        axes[0, 1].axvline(x=self.results['avg_reward'], color='red', 
                          linestyle='--', linewidth=2, label='平均值')
        axes[0, 1].axvline(x=self.results['median_reward'], color='green', 
                          linestyle='--', linewidth=2, label='中位数')
        axes[0, 1].set_xlabel('奖励', fontsize=12)
        axes[0, 1].set_ylabel('频数', fontsize=12)
        axes[0, 1].set_title('奖励分布', fontsize=14, fontweight='bold')
        axes[0, 1].legend()
        axes[0, 1].grid(True, alpha=0.3, axis='y')
        
        # 子图3: 步数曲线
        axes[1, 0].plot(lengths, alpha=0.6, linewidth=1, color='orange')
        axes[1, 0].plot(np.convolve(lengths, np.ones(10)/10, mode='valid'), 
                       color='darkred', linewidth=2, label='移动平均(10)')
        axes[1, 0].set_xlabel('回合', fontsize=12)
        axes[1, 0].set_ylabel('步数', fontsize=12)
        axes[1, 0].set_title('回合步数曲线', fontsize=14, fontweight='bold')
        axes[1, 0].legend()
        axes[1, 0].grid(True, alpha=0.3)
        
        # 子图4: 箱线图
        box_data = [rewards, lengths]
        axes[1, 1].boxplot(box_data, labels=['奖励', '步数'], patch_artist=True,
                          boxprops=dict(facecolor='lightblue', alpha=0.7),
                          medianprops=dict(color='red', linewidth=2))
        axes[1, 1].set_ylabel('数值', fontsize=12)
        axes[1, 1].set_title('统计箱线图', fontsize=14, fontweight='bold')
        axes[1, 1].grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        
        # 保存
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✓ 评估结果图已保存至: {save_path}")
        plt.show()
    
    def save_results(self, save_path: str = 'results/evaluation_metrics.json'):
        """
        保存评估结果到JSON文件
        
        Args:
            save_path: 保存路径
        """
        # 转换numpy类型为Python原生类型
        results_to_save = {
            k: (v.tolist() if isinstance(v, np.ndarray) else 
                float(v) if isinstance(v, np.floating) else v)
            for k, v in self.results.items()
        }
        
        results_to_save['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        results_to_save['environment'] = self.env_name
        
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(results_to_save, f, indent=2, ensure_ascii=False)
        
        print(f"✓ 评估指标已保存至: {save_path}")
    
    def compare_agents(self, agents_config: List[Dict], episodes: int = 50):
        """
        对比多个智能体
        
        Args:
            agents_config: 智能体配置列表
                [{
                    'name': '智能体名称',
                    'agent_type': 'dqn',
                    'buffer_type': 'replay',
                    'model_path': 'path/to/model.pth'
                }, ...]
            episodes: 每个智能体的评估回合数
        """
        comparison_results = {}
        
        print(f"\n{'='*70}")
        print(f"智能体对比评估")
        print(f"{'='*70}\n")
        
        for config in agents_config:
            name = config['name']
            print(f"\n>>> 评估智能体: {name}")
            
            # 创建智能体
            agent, _ = self.create_agent(
                config['agent_type'],
                config['buffer_type']
            )
            
            # 加载模型
            if Path(config['model_path']).exists():
                agent.load(config['model_path'])
                print(f"✓ 已加载模型: {config['model_path']}")
            else:
                print(f"⚠ 模型不存在: {config['model_path']}")
                continue
            
            # 评估
            results = self.evaluate_agent(agent, episodes=episodes, verbose=False)
            comparison_results[name] = results
            
            print(f"  平均奖励: {results['avg_reward']:.2f} ± {results['std_reward']:.2f}")
            print(f"  成功率:   {results['success_rate']:.2f}%")
        
        # 绘制对比图
        self.plot_comparison(comparison_results)
        
        return comparison_results
    
    def plot_comparison(self, comparison_results: Dict, 
                       save_path: str = 'results/agent_comparison.png'):
        """
        绘制智能体对比图
        
        Args:
            comparison_results: 对比结果字典
            save_path: 保存路径
        """
        fig, axes = plt.subplots(1, 3, figsize=(18, 5))
        
        names = list(comparison_results.keys())
        colors = plt.cm.Set3(range(len(names)))
        
        # 子图1: 平均奖励对比
        avg_rewards = [comparison_results[n]['avg_reward'] for n in names]
        std_rewards = [comparison_results[n]['std_reward'] for n in names]
        
        x_pos = np.arange(len(names))
        axes[0].bar(x_pos, avg_rewards, yerr=std_rewards, capsize=5, 
                   alpha=0.7, color=colors, edgecolor='black')
        axes[0].set_xticks(x_pos)
        axes[0].set_xticklabels(names, rotation=15, ha='right')
        axes[0].set_ylabel('平均奖励', fontsize=12)
        axes[0].set_title('平均奖励对比', fontsize=14, fontweight='bold')
        axes[0].grid(True, alpha=0.3, axis='y')
        
        # 子图2: 奖励曲线对比
        for i, name in enumerate(names):
            rewards = comparison_results[name]['episode_rewards']
            smoothed = np.convolve(rewards, np.ones(5)/5, mode='valid')
            axes[1].plot(smoothed, label=name, linewidth=2, color=colors[i])
        
        axes[1].set_xlabel('回合', fontsize=12)
        axes[1].set_ylabel('奖励（平滑）', fontsize=12)
        axes[1].set_title('奖励曲线对比', fontsize=14, fontweight='bold')
        axes[1].legend()
        axes[1].grid(True, alpha=0.3)
        
        # 子图3: 成功率对比
        success_rates = [comparison_results[n]['success_rate'] for n in names]
        axes[2].bar(x_pos, success_rates, alpha=0.7, color=colors, edgecolor='black')
        axes[2].set_xticks(x_pos)
        axes[2].set_xticklabels(names, rotation=15, ha='right')
        axes[2].set_ylabel('成功率 (%)', fontsize=12)
        axes[2].set_title('成功率对比', fontsize=14, fontweight='bold')
        axes[2].set_ylim([0, 105])
        axes[2].grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"\n✓ 对比结果图已保存至: {save_path}")
        plt.show()


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='评估DQN智能体')
    
    parser.add_argument('--env', type=str, default='CartPole-v1',
                       help='环境名称')
    parser.add_argument('--agent', type=str, default='dqn',
                       choices=['dqn', 'double_dqn', 'dueling_dqn'],
                       help='智能体类型')
    parser.add_argument('--buffer', type=str, default='replay',
                       choices=['replay', 'prioritized', 'nstep'],
                       help='缓冲区类型')
    parser.add_argument('--model-path', type=str, 
                       default='checkpoints/dqn_final.pth',
                       help='模型路径')
    parser.add_argument('--episodes', type=int, default=100,
                       help='评估回合数')
    parser.add_argument('--render', action='store_true',
                       help='是否渲染')
    parser.add_argument('--compare', action='store_true',
                       help='对比模式')
    parser.add_argument('--save-results', action='store_true',
                       help='保存结果')
    
    return parser.parse_args()


def main():
    """主函数"""
    args = parse_args()
    
    # 创建评估器
    evaluator = Evaluator(env_name=args.env)
    
    if args.compare:
        # 对比模式
        agents_config = [
            {
                'name': 'DQN + Replay',
                'agent_type': 'dqn',
                'buffer_type': 'replay',
                'model_path': 'checkpoints/dqn_final.pth'
            },
            {
                'name': 'Double DQN + PER',
                'agent_type': 'double_dqn',
                'buffer_type': 'prioritized',
                'model_path': 'checkpoints/double_dqn_final.pth'
            },
            {
                'name': 'Dueling DQN + N-Step',
                'agent_type': 'dueling_dqn',
                'buffer_type': 'nstep',
                'model_path': 'checkpoints/dueling_dqn_final.pth'
            }
        ]
        
        evaluator.compare_agents(agents_config, episodes=args.episodes)
    
    else:
        # 单个智能体评估
        print(f"\n{'='*70}")
        print(f"评估配置")
        print(f"{'='*70}")
        print(f"环境:      {args.env}")
        print(f"智能体:    {args.agent.upper()}")
        print(f"缓冲区:    {args.buffer.upper()}")
        print(f"模型路径:  {args.model_path}")
        print(f"评估回合:  {args.episodes}")
        print(f"{'='*70}")
        
        # 创建智能体
        agent, _ = evaluator.create_agent(args.agent, args.buffer)
        
        # 加载模型
        if Path(args.model_path).exists():
            agent.load(args.model_path)
            print(f"\n✓ 成功加载模型")
        else:
            print(f"\n⚠ 警告: 模型不存在，使用随机初始化")
        
        # 评估
        evaluator.evaluate_agent(agent, episodes=args.episodes, 
                                render=args.render, verbose=True)
        
        # 可视化
        evaluator.plot_results()
        
        # 保存结果
        if args.save_results:
            evaluator.save_results()


if __name__ == '__main__':
    main()