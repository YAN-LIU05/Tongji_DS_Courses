import argparse
import os
import torch
import torch.nn.functional as F
import torch_geometric.transforms as T
import numpy as np
from tqdm import tqdm

from utils import XYGraphP1
from utils_enhanced import add_graph_features
from utils.evaluator import Evaluator
from models.advanced_gnn import HeteroGNN, SupervisedContrastiveGNN


class FocalLoss(torch.nn.Module):
    """Focal Loss用于处理类别不平衡"""
    def __init__(self, alpha=0.25, gamma=2.0):
        super().__init__()
        self.alpha = alpha
        self.gamma = gamma
        
    def forward(self, inputs, targets):
        # 添加数值稳定性
        inputs = torch.clamp(inputs, min=-10, max=10)
        ce_loss = F.cross_entropy(inputs, targets, reduction='none')
        pt = torch.exp(-ce_loss)
        pt = torch.clamp(pt, min=1e-7, max=1.0)
        focal_loss = self.alpha * (1 - pt) ** self.gamma * ce_loss
        return focal_loss.mean()


class EarlyStopping:
    """早停机制"""
    def __init__(self, patience=50, min_delta=0.0001):
        self.patience = patience
        self.min_delta = min_delta
        self.counter = 0
        self.best_score = None
        self.early_stop = False
        
    def __call__(self, val_score):
        if self.best_score is None:
            self.best_score = val_score
        elif val_score < self.best_score + self.min_delta:
            self.counter += 1
            if self.counter >= self.patience:
                self.early_stop = True
        else:
            self.best_score = val_score
            self.counter = 0


def check_model_health(model):
    """检查模型参数健康状况"""
    for name, param in model.named_parameters():
        if param.grad is not None:
            grad_norm = param.grad.norm().item()
            if grad_norm > 100:  # 梯度过大
                return False, f"梯度爆炸: {name}, norm={grad_norm}"
        
        param_norm = param.norm().item()
        if param_norm > 1000:  # 参数过大
            return False, f"参数过大: {name}, norm={param_norm}"
        
        if torch.isnan(param).any() or torch.isinf(param).any():
            return False, f"参数异常: {name}"
    
    return True, "模型健康"


def train_with_contrastive(model, data, train_idx, optimizer, use_focal=True):
    """结合对比学习的训练 - 增强数值稳定性"""
    model.train()
    
    try:
        # 对比学习
        z = model(data.x, data.adj_t, return_embedding=True)
        
        # 检查embedding范数
        z_norm = z.norm(dim=1).mean().item()
        if z_norm > 100 or torch.isnan(z).any() or torch.isinf(z).any():
            print(f"嵌入向量异常 (norm={z_norm:.2f})，重置优化器")
            optimizer.zero_grad()
            return None
        
        # L2正则化embedding
        z = F.normalize(z, p=2, dim=1)
        
        contrastive_loss = model.supervised_contrastive_loss(z[train_idx], data.y[train_idx])
        
        if torch.isnan(contrastive_loss) or torch.isinf(contrastive_loss):
            print("对比损失异常，跳过")
            optimizer.zero_grad()
            return None
        
        # 分类损失
        out = model(data.x, data.adj_t)[train_idx]
        
        # 严格限制输出范围
        out = torch.clamp(out, min=-20, max=20)
        
        y = data.y[train_idx]
        
        if use_focal:
            focal_criterion = FocalLoss()
            classification_loss = focal_criterion(out, y)
        else:
            classification_loss = F.nll_loss(out, y)
        
        if torch.isnan(classification_loss) or torch.isinf(classification_loss):
            print("分类损失异常，跳过")
            optimizer.zero_grad()
            return None
        
        # 总损失 - 减小对比损失权重
        loss = classification_loss + 0.01 * contrastive_loss
        
        optimizer.zero_grad()
        loss.backward()
        
        # 更激进的梯度裁剪
        total_norm = torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=0.5)
        
        if total_norm > 10:
            print(f"梯度过大 (norm={total_norm:.2f})，跳过更新")
            optimizer.zero_grad()
            return None
        
        # 检查模型健康
        is_healthy, msg = check_model_health(model)
        if not is_healthy:
            print(f"模型异常: {msg}，跳过更新")
            optimizer.zero_grad()
            return None
        
        optimizer.step()
        
        return loss.item()
        
    except Exception as e:
        print(f"训练异常: {e}")
        optimizer.zero_grad()
        return None


def train_hetero(model, data, train_idx, optimizer, use_focal=True):
    """异构GNN训练 - 增强数值稳定性"""
    model.train()
    
    try:
        out = model(data.x, data.adj_t, data.y, data.train_mask)[train_idx]
        
        # 严格限制输出范围
        out = torch.clamp(out, min=-20, max=20)
        
        # 检查输出
        if torch.isnan(out).any() or torch.isinf(out).any():
            print("模型输出异常，跳过")
            optimizer.zero_grad()
            return None
        
        y = data.y[train_idx]
        
        if use_focal:
            focal_criterion = FocalLoss()
            loss = focal_criterion(out, y)
        else:
            loss = F.nll_loss(out, y)
        
        if torch.isnan(loss) or torch.isinf(loss):
            print("损失异常，跳过")
            optimizer.zero_grad()
            return None
        
        optimizer.zero_grad()
        loss.backward()
        
        # 更激进的梯度裁剪
        total_norm = torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=0.5)
        
        if total_norm > 10:
            print(f"梯度过大 (norm={total_norm:.2f})，跳过更新")
            optimizer.zero_grad()
            return None
        
        # 检查模型健康
        is_healthy, msg = check_model_health(model)
        if not is_healthy:
            print(f"模型异常: {msg}，跳过更新")
            optimizer.zero_grad()
            return None
        
        optimizer.step()
        
        return loss.item()
        
    except Exception as e:
        print(f"训练异常: {e}")
        optimizer.zero_grad()
        return None


@torch.no_grad()
def test(model, data, split_idx, evaluator):
    """评估模型 - 增强数值稳定性"""
    model.eval()
    
    try:
        out = model(data.x, data.adj_t)
        
        # 严格限制输出
        out = torch.clamp(out, min=-20, max=20)
        
        if torch.isnan(out).any() or torch.isinf(out).any():
            print("测试输出异常，返回默认值")
            return 0.5, 0.5
        
        # 使用softmax
        y_pred = F.softmax(out, dim=1)
        
        # 裁剪预测值
        y_pred = torch.clamp(y_pred, min=1e-7, max=1-1e-7)
        
        train_auc = evaluator.eval(
            data.y[split_idx['train']],
            y_pred[split_idx['train']]
        )['auc']
        
        valid_auc = evaluator.eval(
            data.y[split_idx['valid']],
            y_pred[split_idx['valid']]
        )['auc']
        
        return train_auc, valid_auc
        
    except Exception as e:
        print(f"评估异常: {e}")
        return 0.5, 0.5


def reset_model_weights(model):
    """重置模型权重"""
    def init_weights(m):
        if isinstance(m, torch.nn.Linear):
            torch.nn.init.xavier_uniform_(m.weight, gain=0.1)  # 更小的初始化
            if m.bias is not None:
                torch.nn.init.zeros_(m.bias)
        elif isinstance(m, torch.nn.LayerNorm):
            torch.nn.init.ones_(m.weight)
            torch.nn.init.zeros_(m.bias)
    
    model.apply(init_weights)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--device', type=int, default=0)
    parser.add_argument('--dataset', type=str, default='XYGraphP1')
    parser.add_argument('--model', type=str, default='hetero',
                       choices=['hetero', 'contrastive'])
    parser.add_argument('--epochs', type=int, default=1000)
    parser.add_argument('--lr', type=float, default=0.0005)  # 降低学习率
    parser.add_argument('--hidden_channels', type=int, default=128)  # 减小模型大小
    parser.add_argument('--num_layers', type=int, default=2)  # 减少层数
    parser.add_argument('--dropout', type=float, default=0.5)
    parser.add_argument('--use_focal', action='store_true', default=True)
    parser.add_argument('--use_label_prop', action='store_true', default=False)  # 先关闭
    parser.add_argument('--patience', type=int, default=100)
    parser.add_argument('--runs', type=int, default=5)
    
    args = parser.parse_args()
    print(args)
    
    device = f'cuda:{args.device}' if torch.cuda.is_available() else 'cpu'
    device = torch.device(device)
    
    # 加载数据
    dataset = XYGraphP1(root='./data', name='xydata', transform=T.ToSparseTensor())
    data = dataset[0]
    data.adj_t = data.adj_t.to_symmetric()
    
    # 特征工程
    print('添加图特征...')
    try:
        data = add_graph_features(data)
    except Exception as e:
        print(f"警告: 添加图特征时出错: {e}")
        print("继续执行，不添加额外的图特征...")
    
    # 更稳健的特征标准化
    print('标准化特征...')
    x = data.x
    
    # 移除异常值
    x = torch.nan_to_num(x, nan=0.0, posinf=0.0, neginf=0.0)
    
    # 使用RobustScaler思想
    median = x.median(0)[0]
    q75 = x.quantile(0.75, dim=0)
    q25 = x.quantile(0.25, dim=0)
    iqr = q75 - q25
    iqr[iqr < 1e-6] = 1.0
    
    x = (x - median) / iqr
    
    # 再次裁剪
    x = torch.clamp(x, min=-10, max=10)
    x = torch.nan_to_num(x, nan=0.0, posinf=0.0, neginf=0.0)
    
    data.x = x
    
    if data.y.dim() == 2:
        data.y = data.y.squeeze(1)
    
    split_idx = {
        'train': data.train_mask,
        'valid': data.valid_mask,
        'test': data.test_mask
    }
    
    data = data.to(device)
    
    evaluator = Evaluator('auc')
    
    # 多次运行
    test_aucs = []
    
    for run in range(args.runs):
        print(f'\n{"="*50}')
        print(f'第 {run + 1}/{args.runs} 次运行')
        print(f'{"="*50}')
        
        # 设置随机种子
        torch.manual_seed(run + 42)
        np.random.seed(run + 42)
        if torch.cuda.is_available():
            torch.cuda.manual_seed(run + 42)
        
        # 创建模型
        if args.model == 'hetero':
            model = HeteroGNN(
                in_channels=data.x.size(-1),
                hidden_channels=args.hidden_channels,
                out_channels=2,
                num_layers=args.num_layers,
                dropout=args.dropout,
                use_transformer=False,  # 先关闭transformer
                use_label_prop=args.use_label_prop
            ).to(device)
        else:
            model = SupervisedContrastiveGNN(
                in_channels=data.x.size(-1),
                hidden_channels=args.hidden_channels,
                out_channels=2,
                num_layers=args.num_layers,
                dropout=args.dropout
            ).to(device)
        
        # 重置权重
        reset_model_weights(model)
        
        # 使用更保守的优化器设置
        optimizer = torch.optim.AdamW(
            model.parameters(),
            lr=args.lr,
            weight_decay=1e-5,  # 减小权重衰减
            eps=1e-8
        )
        
        scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
            optimizer, mode='max', factor=0.5, patience=30, 
            verbose=True, min_lr=1e-6
        )
        
        early_stopping = EarlyStopping(patience=args.patience)
        
        best_valid_auc = 0
        best_epoch = 0
        consecutive_fails = 0  # 连续失败计数
        
        pbar = tqdm(range(1, args.epochs + 1), desc=f'第{run + 1}次运行')
        for epoch in pbar:
            if args.model == 'hetero':
                loss = train_hetero(model, data, split_idx['train'], optimizer, args.use_focal)
            else:
                loss = train_with_contrastive(model, data, split_idx['train'], optimizer, args.use_focal)
            
            # 处理训练失败
            if loss is None:
                consecutive_fails += 1
                if consecutive_fails > 10:
                    print(f"\n连续{consecutive_fails}次训练失败，重置模型")
                    reset_model_weights(model)
                    consecutive_fails = 0
                    # 降低学习率
                    for param_group in optimizer.param_groups:
                        param_group['lr'] *= 0.5
                continue
            
            consecutive_fails = 0  # 重置失败计数
            
            train_auc, valid_auc = test(model, data, split_idx, evaluator)
            
            scheduler.step(valid_auc)
            
            if valid_auc > best_valid_auc:
                best_valid_auc = valid_auc
                best_epoch = epoch
                
                # 保存最佳模型
                save_dir = f'./model_files/{args.dataset}/{args.model}_run{run}'
                os.makedirs(save_dir, exist_ok=True)
                torch.save(model.state_dict(), f'{save_dir}/model.pt')
            
            pbar.set_postfix({
                '损失': f'{loss:.4f}',
                '训练': f'{train_auc:.4f}',
                '验证': f'{valid_auc:.4f}',
                '最佳': f'{best_valid_auc:.4f}'
            })
            
            early_stopping(valid_auc)
            if early_stopping.early_stop:
                print(f'\n在第{epoch}轮早停')
                break
        
        print(f'\n第{run + 1}次运行完成!')
        print(f'最佳验证AUC: {best_valid_auc:.4f}，在第{best_epoch}轮')
        test_aucs.append(best_valid_auc)
    
    print(f'\n{"="*50}')
    print(f'{args.runs}次运行的最终结果:')
    print(f'平均验证AUC: {np.mean(test_aucs):.4f} ± {np.std(test_aucs):.4f}')
    print(f'{"="*50}')


if __name__ == '__main__':
    main()