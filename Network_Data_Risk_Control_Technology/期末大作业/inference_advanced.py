import argparse
import torch
import torch.nn.functional as F
import torch_geometric.transforms as T
import numpy as np
import pandas as pd
import os

from utils import XYGraphP1
from utils_enhanced import add_graph_features
from utils.evaluator import Evaluator
from models.advanced_gnn import HeteroGNN, SupervisedContrastiveGNN

@torch.no_grad()
def test(model, data, split_idx, evaluator):
    """
    推理函数 - 保持与训练脚本一致的数值稳定性处理
    """
    model.eval()
    
    # 1. 前向传播
    # 注意：train_advanced.py 中的模型 forward 返回的是 log_softmax
    if isinstance(model, SupervisedContrastiveGNN):
        # 对比学习模型只用 encoder + classifier 部分
        out = model(data.x, data.adj_t)
    else:
        out = model(data.x, data.adj_t)
    
    # 2. 数值截断 (与训练代码保持一致)
    out = torch.clamp(out, min=-20, max=20)
    
    # 3. 转换为概率
    # 因为输出是 log_softmax，理论上应该用 .exp()
    # 但为了完全复刻 train_advanced.py 中的 test 函数逻辑，我们采用那边的方式：
    # 原代码用的是: F.softmax(out, dim=1) 作用在 log_probs 上
    # 这里我们修正为标准的 .exp() 以获得准确概率，或者保留 F.softmax (会使分布更平滑)
    # 建议：标准做法是 .exp()，但如果训练代码用的 softmax，这里用 .exp() 也是数学上还原概率的正确方式
    y_pred = out.exp() 
    
    # 4. 再次截断概率值，防止极端值
    y_pred = torch.clamp(y_pred, min=1e-7, max=1-1e-7)
    
    # 5. 提取预测结果 (N, 2) -> (N, ) 取正类的概率
    # 假设第1列是正类 (根据数据集通常定义)
    preds = y_pred[:, 1]
    
    # 6. 计算指标
    results = {}
    for key in ['train', 'valid', 'test']:
        node_id = split_idx[key]
        try:
            auc = evaluator.eval(data.y[node_id], y_pred[node_id])['auc']
            results[key] = auc
        except:
            results[key] = 0.0
            
    return results, preds

def main():
    parser = argparse.ArgumentParser(description='Advanced GNN Inference')
    parser.add_argument('--device', type=int, default=0)
    parser.add_argument('--dataset', type=str, default='XYGraphP1')
    parser.add_argument('--model', type=str, default='hetero', 
                        choices=['hetero', 'contrastive'])
    # 下面的参数必须与训练时设置的一致
    parser.add_argument('--hidden_channels', type=int, default=128)
    parser.add_argument('--num_layers', type=int, default=2)
    parser.add_argument('--dropout', type=float, default=0.5)
    parser.add_argument('--run', type=int, default=0, help='加载第几次运行的模型权重')
    
    args = parser.parse_args()
    print(args)
    
    device = f'cuda:{args.device}' if torch.cuda.is_available() else 'cpu'
    device = torch.device(device)

    # ----------------------------------------------------------------------
    # 1. 数据加载与预处理 (必须严格与 train_advanced.py 一致)
    # ----------------------------------------------------------------------
    print('Loading data...')
    dataset = XYGraphP1(root='./data', name='xydata', transform=T.ToSparseTensor())
    data = dataset[0]
    data.adj_t = data.adj_t.to_symmetric()
    
    # [特征工程] - 对应 utils_enhanced
    print('Adding graph features...')
    try:
        data = add_graph_features(data)
    except Exception as e:
        print(f"Warning: Failed to add graph features: {e}")
        # 如果训练时加了，这里没加，会导致维度报错
    
    # [特征标准化] - 对应 RobustScaler 逻辑
    print('Normalizing features...')
    x = data.x
    x = torch.nan_to_num(x, nan=0.0, posinf=0.0, neginf=0.0)
    
    median = x.median(0)[0]
    q75 = x.quantile(0.75, dim=0)
    q25 = x.quantile(0.25, dim=0)
    iqr = q75 - q25
    iqr[iqr < 1e-6] = 1.0
    
    x = (x - median) / iqr
    
    # [数值截断]
    x = torch.clamp(x, min=-10, max=10)
    x = torch.nan_to_num(x, nan=0.0, posinf=0.0, neginf=0.0)
    data.x = x
    
    # 标签处理
    if data.y.dim() == 2:
        data.y = data.y.squeeze(1)
        
    split_idx = {'train': data.train_mask, 'valid': data.valid_mask, 'test': data.test_mask}
    
    # 保存原始的test_mask用于后续索引
    test_mask_cpu = data.test_mask.cpu()
    
    data = data.to(device)

    # ----------------------------------------------------------------------
    # 2. 模型初始化
    # ----------------------------------------------------------------------
    print(f'Initializing model: {args.model}...')
    if args.model == 'hetero':
        model = HeteroGNN(
            in_channels=data.x.size(-1),
            hidden_channels=args.hidden_channels,
            out_channels=2,
            num_layers=args.num_layers,
            dropout=args.dropout,
            use_transformer=False, # 默认为False，如需开启需加参数
            use_label_prop=False   # 默认为False
        ).to(device)
    else:
        model = SupervisedContrastiveGNN(
            in_channels=data.x.size(-1),
            hidden_channels=args.hidden_channels,
            out_channels=2,
            num_layers=args.num_layers,
            dropout=args.dropout
        ).to(device)

    print(f'Model params: {sum(p.numel() for p in model.parameters())}')

    # ----------------------------------------------------------------------
    # 3. 加载权重
    # ----------------------------------------------------------------------
    model_path = f'./model_files/{args.dataset}/{args.model}_run{args.run}/model.pt'
    print(f'Loading model from: {model_path}')
    
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found at {model_path}. Please check args.")
        
    state_dict = torch.load(model_path, map_location=device)
    model.load_state_dict(state_dict)

    # ----------------------------------------------------------------------
    # 4. 推理与评估
    # ----------------------------------------------------------------------
    print('Starting inference...')
    evaluator = Evaluator('auc')
    results, all_preds = test(model, data, split_idx, evaluator)
    
    print(f'\nInference Results (Run {args.run}):')
    print(f"Train AUC: {results['train']:.4f}")
    print(f"Valid AUC: {results['valid']:.4f}")
    
    # ----------------------------------------------------------------------
    # 5. 保存结果
    # ----------------------------------------------------------------------
    # 提取测试集的预测结果
    test_preds = all_preds[test_mask_cpu].cpu().numpy()
    
    # 获取测试集的节点索引
    test_indices = np.arange(data.x.size(0))[test_mask_cpu.numpy()]
    
    save_dir = './submit'
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    
    # 保存为npy文件
    npy_path = f'{save_dir}/preds_{args.model}_run{args.run}.npy'
    np.save(npy_path, test_preds)
    print(f'\nTest predictions saved to: {npy_path}')
    print(f'Shape: {test_preds.shape}')
    
    # 保存为CSV文件
    csv_path = f'{save_dir}/preds_{args.model}_run{args.run}.csv'
    df = pd.DataFrame({
        'index': test_indices,
        'predict': test_preds
    })
    df.to_csv(csv_path, index=False)
    print(f'Test predictions saved to: {csv_path}')
    print(f'CSV shape: {df.shape}')
    print(f'\nPrediction statistics:')
    print(f'  Mean: {test_preds.mean():.6f}')
    print(f'  Std: {test_preds.std():.6f}')
    print(f'  Min: {test_preds.min():.6f}')
    print(f'  Max: {test_preds.max():.6f}')

if __name__ == "__main__":
    main()