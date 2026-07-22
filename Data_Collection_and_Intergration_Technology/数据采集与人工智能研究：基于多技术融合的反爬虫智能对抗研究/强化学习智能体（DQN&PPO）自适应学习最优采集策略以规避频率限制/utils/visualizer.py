"""
训练可视化工具
"""
import matplotlib.pyplot as plt
import numpy as np
import os
from matplotlib import font_manager

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

class Visualizer:
    """训练过程可视化"""
    
    def __init__(self, results_dir):
        self.results_dir = results_dir
        os.makedirs(results_dir, exist_ok=True)
    
    def plot_training_curves(self, rewards, success_rates, steps, losses):
        """绘制训练曲线"""
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        
        # 1. 奖励曲线
        self._plot_curve(axes[0, 0], rewards, 
                        '回合奖励', 'Episode', 'Total Reward',
                        color='blue', smooth_window=10)
        
        # 2. 成功率曲线
        self._plot_curve(axes[0, 1], 
                        [r * 100 for r in success_rates],
                        '成功率', 'Episode', 'Success Rate (%)',
                        color='green', smooth_window=10)
        
        # 3. 步数曲线
        self._plot_curve(axes[1, 0], steps,
                        '回合步数', 'Episode', 'Steps',
                        color='orange', smooth_window=10)
        
        # 4. 损失曲线
        if losses:
            self._plot_curve(axes[1, 1], losses,
                            '训练损失', 'Episode', 'Loss',
                            color='red', smooth_window=10)
        
        plt.tight_layout()
        save_path = os.path.join(self.results_dir, 'training_curves.png')
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✓ 训练曲线已保存: {save_path}")
    
    def _plot_curve(self, ax, data, title, xlabel, ylabel, 
                   color='blue', smooth_window=10):
        """绘制单条曲线"""
        episodes = range(len(data))
        
        # 原始数据
        ax.plot(episodes, data, alpha=0.3, color=color, linewidth=0.5)
        
        # 平滑曲线
        if len(data) >= smooth_window:
            smoothed = self._smooth(data, smooth_window)
            ax.plot(episodes, smoothed, color=color, linewidth=2, 
                   label=f'Smoothed ({smooth_window})')
            ax.legend()
        
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xlabel(xlabel, fontsize=12)
        ax.set_ylabel(ylabel, fontsize=12)
        ax.grid(True, alpha=0.3)
    
    def _smooth(self, data, window):
        """移动平均平滑"""
        if len(data) < window:
            return data
        
        smoothed = []
        for i in range(len(data)):
            start = max(0, i - window // 2)
            end = min(len(data), i + window // 2 + 1)
            smoothed.append(np.mean(data[start:end]))
        
        return smoothed
    
    def plot_action_distribution(self, action_counts, action_names):
        """绘制动作分布"""
        fig, ax = plt.subplots(figsize=(12, 6))
        
        actions = list(action_counts.keys())
        counts = list(action_counts.values())
        
        bars = ax.bar(actions, counts, color='steelblue', alpha=0.7)
        
        # 添加数值标签
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{int(height)}',
                   ha='center', va='bottom', fontsize=10)
        
        ax.set_title('动作选择分布', fontsize=14, fontweight='bold')
        ax.set_xlabel('Action ID', fontsize=12)
        ax.set_ylabel('Count', fontsize=12)
        ax.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        save_path = os.path.join(self.results_dir, 'action_distribution.png')
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✓ 动作分布图已保存: {save_path}")