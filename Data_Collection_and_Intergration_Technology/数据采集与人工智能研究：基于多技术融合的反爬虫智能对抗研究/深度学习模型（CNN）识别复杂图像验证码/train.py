"""
改进的训练脚本 - 使用更好的训练策略
"""
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torch.optim.lr_scheduler import CosineAnnealingLR, ReduceLROnPlateau
from tqdm import tqdm
import os
import matplotlib.pyplot as plt
import numpy as np

import config
from utils.dataset import CaptchaDataset
from models.model import LightweightCaptchaCNN

class AdvancedTrainer:
    def __init__(self, model_class=LightweightCaptchaCNN):
        print("="*60)
        print("初始化高级训练器")
        print("="*60)
        
        # 数据加载
        print("加载数据集...")
        train_dataset = CaptchaDataset(config.TRAIN_DIR, config.CHARSET, augment=True)
        val_dataset = CaptchaDataset(config.VAL_DIR, config.CHARSET, augment=False)
        
        self.train_loader = DataLoader(
            train_dataset,
            batch_size=config.BATCH_SIZE,
            shuffle=True,
            num_workers=0,
            pin_memory=True if torch.cuda.is_available() else False,
            drop_last=True
        )
        
        self.val_loader = DataLoader(
            val_dataset,
            batch_size=config.BATCH_SIZE,
            shuffle=False,
            num_workers=0,
            pin_memory=True if torch.cuda.is_available() else False
        )
        
        # 模型
        print(f"创建模型 (设备: {config.DEVICE})...")
        self.model = model_class(
            num_classes=len(config.CHARSET),
            num_chars=config.NUM_CHARS
        ).to(config.DEVICE)
        
        # 打印模型信息
        total_params = sum(p.numel() for p in self.model.parameters())
        print(f"模型参数总数: {total_params:,}")
        
        # Label Smoothing损失函数
        self.criterion = nn.CrossEntropyLoss(label_smoothing=0.1)
        
        # AdamW优化器
        self.optimizer = optim.AdamW(
            self.model.parameters(),
            lr=config.LEARNING_RATE,
            weight_decay=0.01
        )
        
        # 改用余弦退火调度器（不重启）
        self.scheduler = CosineAnnealingLR(
            self.optimizer,
            T_max=config.NUM_EPOCHS,
            eta_min=1e-6
        )
        
        # 记录学习率变化
        self.learning_rates = []
        
        # 记录
        self.train_losses = []
        self.train_accs = []
        self.val_accuracies = []
        self.best_acc = 0.0
        self.idx_to_char = {idx: char for idx, char in enumerate(config.CHARSET)}
        
        # 创建目录
        os.makedirs(config.CHECKPOINT_DIR, exist_ok=True)
        os.makedirs(config.RESULTS_DIR, exist_ok=True)
        
        print(f"训练集: {len(train_dataset)}, 验证集: {len(val_dataset)}")
        print(f"Batch size: {config.BATCH_SIZE}")
        print(f"字符集大小: {len(config.CHARSET)}")
        print(f"学习率调度: CosineAnnealingLR (平滑衰减)")
        print("="*60)
    
    def train_epoch(self, epoch):
        self.model.train()
        total_loss = 0
        correct_chars = 0
        total_chars = 0
        
        pbar = tqdm(self.train_loader, desc=f'Epoch {epoch+1}/{config.NUM_EPOCHS}')
        
        for batch_idx, (images, labels) in enumerate(pbar):
            images = images.to(config.DEVICE)
            labels = labels.to(config.DEVICE)
            
            self.optimizer.zero_grad()
            
            # 前向传播
            outputs = self.model(images)
            
            # 计算损失
            loss = 0
            for i in range(len(outputs)):
                loss += self.criterion(outputs[i], labels[:, i])
            loss = loss / len(outputs)
            
            # 反向传播
            loss.backward()
            
            # 梯度裁剪
            torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
            
            self.optimizer.step()
            
            # 统计准确率
            with torch.no_grad():
                for i in range(len(outputs)):
                    preds = torch.argmax(outputs[i], dim=1)
                    correct_chars += (preds == labels[:, i]).sum().item()
                    total_chars += labels.size(0)
            
            total_loss += loss.item()
            
            # 更新进度条
            char_acc = 100 * correct_chars / total_chars
            pbar.set_postfix({
                'loss': f'{loss.item():.4f}',
                'char_acc': f'{char_acc:.2f}%',
                'lr': f'{self.optimizer.param_groups[0]["lr"]:.6f}'
            })
        
        avg_loss = total_loss / len(self.train_loader)
        train_acc = 100 * correct_chars / total_chars
        
        return avg_loss, train_acc
    
    def validate(self):
        self.model.eval()
        correct = 0
        total = 0
        char_correct = [0] * config.NUM_CHARS
        char_total = [0] * config.NUM_CHARS
        
        all_preds = []
        all_labels = []
        
        with torch.no_grad():
            for images, labels in tqdm(self.val_loader, desc='Validating'):
                images = images.to(config.DEVICE)
                labels = labels.to(config.DEVICE)
                
                outputs = self.model(images)
                
                # 获取预测
                predictions = [torch.argmax(output, dim=1) for output in outputs]
                predictions = torch.stack(predictions, dim=1)
                
                # 整体准确率
                correct += (predictions == labels).all(dim=1).sum().item()
                total += labels.size(0)
                
                # 每个位置准确率
                for i in range(config.NUM_CHARS):
                    char_correct[i] += (predictions[:, i] == labels[:, i]).sum().item()
                    char_total[i] += labels.size(0)
                
                # 保存用于分析
                all_preds.extend(predictions.cpu().numpy())
                all_labels.extend(labels.cpu().numpy())
        
        accuracy = 100 * correct / total
        char_accuracies = [100 * char_correct[i] / char_total[i] 
                          for i in range(config.NUM_CHARS)]
        
        return accuracy, char_accuracies, all_preds, all_labels
    
    def train(self):
        print(f"\n开始训练 {config.NUM_EPOCHS} 个epoch")
        print("-" * 60)
        
        for epoch in range(config.NUM_EPOCHS):
            # 训练
            train_loss, train_acc = self.train_epoch(epoch)
            self.train_losses.append(train_loss)
            self.train_accs.append(train_acc)
            
            # 验证
            val_acc, char_accs, preds, labels = self.validate()
            self.val_accuracies.append(val_acc)
            
            # 记录学习率
            current_lr = self.optimizer.param_groups[0]['lr']
            self.learning_rates.append(current_lr)
            
            # 更新学习率
            self.scheduler.step()
            
            print(f"\nEpoch {epoch+1}/{config.NUM_EPOCHS}:")
            print(f"  训练损失: {train_loss:.4f}")
            print(f"  训练字符准确率: {train_acc:.2f}%")
            print(f"  验证整体准确率: {val_acc:.2f}%")
            print(f"  验证各位准确率: {[f'{acc:.1f}%' for acc in char_accs]}")
            print(f"  学习率: {current_lr:.6f}")
            
            # 保存最佳模型
            if val_acc > self.best_acc:
                self.best_acc = val_acc
                torch.save({
                    'epoch': epoch,
                    'model_state_dict': self.model.state_dict(),
                    'optimizer_state_dict': self.optimizer.state_dict(),
                    'accuracy': val_acc,
                    'char_accuracies': char_accs,
                }, os.path.join(config.CHECKPOINT_DIR, f'best_model_{val_acc:.2f}.pth'))
                print(f"  ✓ 保存最佳模型")
            
            # 定期保存
            if (epoch + 1) % 5 == 0:
                torch.save({
                    'epoch': epoch,
                    'model_state_dict': self.model.state_dict(),
                    'optimizer_state_dict': self.optimizer.state_dict(),
                    'accuracy': val_acc,
                }, os.path.join(config.CHECKPOINT_DIR, f'checkpoint_epoch_{epoch+1}.pth'))
            
            print("-" * 60)
        
        print(f"\n训练完成！最佳准确率: {self.best_acc:.2f}%")
        self.plot_history()
    
    def plot_history(self):
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # 损失曲线
        axes[0, 0].plot(self.train_losses, label='Train Loss', linewidth=2)
        axes[0, 0].set_title('Training Loss', fontsize=14, fontweight='bold')
        axes[0, 0].set_xlabel('Epoch')
        axes[0, 0].set_ylabel('Loss')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)
        
        # 训练准确率
        axes[0, 1].plot(self.train_accs, label='Train Char Acc', linewidth=2, color='green')
        axes[0, 1].set_title('Training Character Accuracy', fontsize=14, fontweight='bold')
        axes[0, 1].set_xlabel('Epoch')
        axes[0, 1].set_ylabel('Accuracy (%)')
        axes[0, 1].legend()
        axes[0, 1].grid(True, alpha=0.3)
        
        # 验证准确率
        axes[1, 0].plot(self.val_accuracies, label='Val Overall Acc', linewidth=2, color='orange')
        axes[1, 0].set_title('Validation Overall Accuracy', fontsize=14, fontweight='bold')
        axes[1, 0].set_xlabel('Epoch')
        axes[1, 0].set_ylabel('Accuracy (%)')
        axes[1, 0].legend()
        axes[1, 0].grid(True, alpha=0.3)
        
        # 学习率变化
        axes[1, 1].plot(self.learning_rates, label='Learning Rate', linewidth=2, color='red')
        axes[1, 1].set_title('Learning Rate Schedule', fontsize=14, fontweight='bold')
        axes[1, 1].set_xlabel('Epoch')
        axes[1, 1].set_ylabel('Learning Rate')
        axes[1, 1].set_yscale('log')  # 使用对数坐标
        axes[1, 1].legend()
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(os.path.join(config.RESULTS_DIR, 'training_history.png'), dpi=300)
        print(f"训练曲线已保存")

if __name__ == '__main__':
    trainer = AdvancedTrainer()
    trainer.train()