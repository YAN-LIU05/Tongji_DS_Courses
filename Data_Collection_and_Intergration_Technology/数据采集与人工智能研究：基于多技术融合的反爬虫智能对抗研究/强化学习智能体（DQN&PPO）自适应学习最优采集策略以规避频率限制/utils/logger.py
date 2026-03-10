"""
训练日志记录器
"""
import os
import json
from datetime import datetime
import csv

class Logger:
    """训练日志记录"""
    
    def __init__(self, log_dir):
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        
        # 创建日志文件
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.log_file = os.path.join(log_dir, f'training_{timestamp}.log')
        self.csv_file = os.path.join(log_dir, f'metrics_{timestamp}.csv')
        
        # 初始化CSV
        with open(self.csv_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'episode', 'total_reward', 'steps', 'success_rate',
                'loss', 'requests_per_second', 'banned_ips', 'risk_score'
            ])
        
        self.log(f"日志初始化 - {timestamp}")
    
    def log(self, message):
        """写入日志"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"[{timestamp}] {message}"
        
        with open(self.log_file, 'a') as f:
            f.write(log_message + '\n')
        
        print(log_message)
    
    def log_episode(self, episode, stats):
        """记录回合统计"""
        # 写入CSV
        with open(self.csv_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                episode,
                stats['total_reward'],
                stats['steps'],
                stats['success_rate'],
                stats.get('loss', 0),
                stats['requests_per_second'],
                stats['banned_ips'],
                stats['risk_score']
            ])
        
        # 详细日志
        if (episode + 1) % 50 == 0:
            self.log(f"Episode {episode + 1}: Reward={stats['total_reward']:.2f}, "
                    f"Success={stats['success_rate']:.2%}, "
                    f"Steps={stats['steps']}")