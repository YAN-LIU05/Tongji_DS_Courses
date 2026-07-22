import torch
import torch.nn.functional as F
from torch.nn import Linear, BatchNorm1d, ModuleList, Dropout, LayerNorm
from torch_geometric.nn import GCNConv, SAGEConv, GATConv, GINConv
from torch_geometric.utils import dropout_edge, add_self_loops, degree
import math


class AdaptiveMessagePassing(torch.nn.Module):
    """自适应消息传递层"""
    def __init__(self, in_channels, out_channels):
        super().__init__()
        self.lin_src = Linear(in_channels, out_channels)
        self.lin_dst = Linear(in_channels, out_channels)
        self.lin_edge = Linear(in_channels * 2, out_channels)
        self.gate = Linear(out_channels * 3, 3)
        
    def forward(self, x, edge_index):
        row, col = edge_index
        
        # 源节点、目标节点和边特征
        x_src = self.lin_src(x[row])
        x_dst = self.lin_dst(x[col])
        x_edge = self.lin_edge(torch.cat([x[row], x[col]], dim=-1))
        
        # 自适应门控
        gate_input = torch.cat([x_src, x_dst, x_edge], dim=-1)
        gates = torch.softmax(self.gate(gate_input), dim=-1)
        
        # 加权聚合
        out = gates[:, 0:1] * x_src + gates[:, 1:2] * x_dst + gates[:, 2:3] * x_edge
        
        # 聚合到目标节点
        out_scatter = torch.zeros(x.size(0), out.size(1), device=x.device)
        out_scatter.index_add_(0, col, out)
        
        return out_scatter


class LabelPropagation(torch.nn.Module):
    """标签传播模块"""
    def __init__(self, num_layers, alpha=0.9):
        super().__init__()
        self.num_layers = num_layers
        self.alpha = alpha
        
    @torch.no_grad()
    def forward(self, y, edge_index, mask, num_classes):
        # 初始化
        out = torch.zeros(y.size(0), num_classes, device=y.device)
        out[mask] = F.one_hot(y[mask], num_classes).float()
        
        # 计算度
        row, col = edge_index
        deg = degree(col, y.size(0), dtype=torch.float)
        deg_inv_sqrt = deg.pow(-0.5)
        deg_inv_sqrt[deg_inv_sqrt == float('inf')] = 0
        
        # 传播
        for _ in range(self.num_layers):
            # 归一化
            out_norm = deg_inv_sqrt.view(-1, 1) * out
            
            # 聚合
            out_new = torch.zeros_like(out)
            out_new.index_add_(0, col, out_norm[row])
            out_new = deg_inv_sqrt.view(-1, 1) * out_new
            
            # 加权更新
            out = self.alpha * out_new + (1 - self.alpha) * out
            
            # 保持标注节点不变
            out[mask] = F.one_hot(y[mask], num_classes).float()
        
        return out


class FeatureAugmentation(torch.nn.Module):
    """特征增强模块"""
    def __init__(self, in_channels, aug_channels):
        super().__init__()
        self.lin1 = Linear(in_channels, aug_channels)
        self.lin2 = Linear(in_channels, aug_channels)
        self.bn = BatchNorm1d(aug_channels * 2)
        
    def forward(self, x):
        # 非线性变换
        x1 = torch.tanh(self.lin1(x))
        x2 = torch.sigmoid(self.lin2(x))
        
        # 拼接
        x_aug = torch.cat([x, x1, x2], dim=-1)
        
        return x_aug


class GraphTransformerLayer(torch.nn.Module):
    """图Transformer层"""
    def __init__(self, channels, num_heads=8, dropout=0.1):
        super().__init__()
        self.num_heads = num_heads
        self.head_dim = channels // num_heads
        
        self.q_proj = Linear(channels, channels)
        self.k_proj = Linear(channels, channels)
        self.v_proj = Linear(channels, channels)
        self.o_proj = Linear(channels, channels)
        
        self.dropout = Dropout(dropout)
        self.layer_norm1 = LayerNorm(channels)
        self.layer_norm2 = LayerNorm(channels)
        
        self.ffn = torch.nn.Sequential(
            Linear(channels, channels * 4),
            torch.nn.GELU(),
            Dropout(dropout),
            Linear(channels * 4, channels),
            Dropout(dropout)
        )
        
    def forward(self, x, edge_index):
        # Multi-head attention
        residual = x
        x = self.layer_norm1(x)
        
        q = self.q_proj(x).view(-1, self.num_heads, self.head_dim)
        k = self.k_proj(x).view(-1, self.num_heads, self.head_dim)
        v = self.v_proj(x).view(-1, self.num_heads, self.head_dim)
        
        # 只在边上计算注意力
        row, col = edge_index
        
        # 计算注意力分数
        attn_score = (q[row] * k[col]).sum(dim=-1) / math.sqrt(self.head_dim)
        attn_weights = torch.softmax(attn_score, dim=0)
        attn_weights = self.dropout(attn_weights)
        
        # 聚合
        out = torch.zeros_like(v)
        for h in range(self.num_heads):
            weighted_v = attn_weights[:, h:h+1] * v[col, h]
            out[:, h].index_add_(0, row, weighted_v)
        
        out = out.view(-1, self.num_heads * self.head_dim)
        out = self.o_proj(out)
        out = self.dropout(out)
        out = out + residual
        
        # FFN
        residual = out
        out = self.layer_norm2(out)
        out = self.ffn(out)
        out = out + residual
        
        return out


class HeteroGNN(torch.nn.Module):
    def __init__(self, in_channels, hidden_channels, out_channels, num_layers,
                 dropout=0.5, use_transformer=False, use_label_prop=False,
                 aug_channels=None):
        super().__init__()
        
        self.num_layers = num_layers
        self.dropout = dropout
        self.use_transformer = use_transformer
        self.use_label_prop = use_label_prop
        
        # Feature augmentation
        if aug_channels is None:
            aug_channels = in_channels
        self.feat_aug = FeatureAugmentation(in_channels, aug_channels)
        
        # 增强后的特征维度：原始 + 两个增强分支
        aug_input_channels = in_channels + aug_channels * 2
        
        # 聚合权重
        self.aggregation_weights = torch.nn.Parameter(torch.ones(4) / 4)
        
        # GNN layers - 4个分支
        self.gcn_convs = torch.nn.ModuleList()
        self.sage_convs = torch.nn.ModuleList()
        self.gat_convs = torch.nn.ModuleList()
        self.gin_convs = torch.nn.ModuleList()
        self.bns = torch.nn.ModuleList()
        
        for i in range(num_layers):
            in_ch = aug_input_channels if i == 0 else hidden_channels * 4
            
            self.gcn_convs.append(GCNConv(in_ch, hidden_channels))
            self.sage_convs.append(SAGEConv(in_ch, hidden_channels))
            self.gat_convs.append(GATConv(in_ch, hidden_channels, heads=8, 
                                         concat=False, dropout=dropout))
            
            gin_nn = torch.nn.Sequential(
                torch.nn.Linear(in_ch, hidden_channels),
                torch.nn.ReLU(),
                torch.nn.Linear(hidden_channels, hidden_channels)
            )
            self.gin_convs.append(GINConv(gin_nn))
            
            self.bns.append(BatchNorm1d(hidden_channels * 4))
        
        # Transformer (可选)
        if use_transformer:
            self.transformer = torch.nn.TransformerEncoderLayer(
                d_model=hidden_channels * 4,
                nhead=8,
                dim_feedforward=hidden_channels * 4,
                dropout=dropout,
                batch_first=True
            )
        
        # Label propagation (可选)
        if use_label_prop:
            self.label_prop = LabelPropagation(num_layers=3, alpha=0.9)
        
        # Output layer
        self.output = torch.nn.Linear(hidden_channels * 4, out_channels)
    
    def forward(self, x, adj_t):
        # Feature augmentation
        x = self.feat_aug(x)
        
        # GNN layers
        for i in range(self.num_layers):
            # 4个分支并行处理
            x_list = []
            x_list.append(self.gcn_convs[i](x, adj_t))
            x_list.append(self.sage_convs[i](x, adj_t))
            x_list.append(self.gat_convs[i](x, adj_t))
            x_list.append(self.gin_convs[i](x, adj_t))
            
            # 拼接所有分支
            x = torch.cat(x_list, dim=-1)
            
            # BN + activation + dropout
            x = self.bns[i](x)
            x = F.relu(x)
            x = F.dropout(x, p=self.dropout, training=self.training)
        
        # Transformer (可选)
        if self.use_transformer:
            x = x.unsqueeze(0)
            x = self.transformer(x)
            x = x.squeeze(0)
        
        # 最终输出
        logits = self.output(x)
        return F.log_softmax(logits, dim=-1)


class SupervisedContrastiveGNN(torch.nn.Module):
    """带有监督对比学习的GNN"""
    def __init__(self, in_channels, hidden_channels, out_channels, num_layers=3, dropout=0.5):
        super().__init__()
        
        self.num_layers = num_layers
        self.dropout = dropout
        
        # Encoder
        self.encoder = HeteroGNN(
            in_channels, hidden_channels, hidden_channels, 
            num_layers, dropout, use_transformer=False, use_label_prop=False
        )
        
        # Projection head for contrastive learning
        self.projection = torch.nn.Sequential(
            Linear(hidden_channels * 4, hidden_channels),
            torch.nn.ReLU(),
            Linear(hidden_channels, 128)
        )
        
        # Classifier
        self.classifier = Linear(hidden_channels * 4, out_channels)
        
    def forward(self, x, edge_index, return_embedding=False):
        # 获取嵌入
        h = self.encoder.feat_aug(x)
        
        if hasattr(edge_index, 'coo'):
            row, col, _ = edge_index.coo()
            edge_index_tuple = torch.stack([row, col], dim=0)
        else:
            edge_index_tuple = edge_index
        
        for i in range(self.num_layers - 1):
            x_gcn = self.encoder.gcn_convs[i](h, edge_index)
            x_sage = self.encoder.sage_convs[i](h, edge_index)
            x_gat = self.encoder.gat_convs[i](h, edge_index_tuple)
            x_gin = self.encoder.gin_convs[i](h, edge_index_tuple)
            
            h = torch.cat([x_gcn, x_sage, x_gat, x_gin], dim=1)
            h = self.encoder.bns[i](h)
            h = F.relu(h)
            h = F.dropout(h, p=self.dropout, training=self.training)
        
        if return_embedding:
            return self.projection(h)
        
        logits = self.classifier(h)
        return F.log_softmax(logits, dim=1)
    
    def supervised_contrastive_loss(self, z, y, temperature=0.07):
        """监督对比损失"""
        # L2归一化
        z = F.normalize(z, p=2, dim=1)
        
        # 计算相似度矩阵
        sim_matrix = torch.matmul(z, z.t()) / temperature
        
        # 创建标签mask
        y_expanded = y.unsqueeze(1)
        positive_mask = (y_expanded == y_expanded.t()).float()
        
        # 对角线设为0（排除自己）
        positive_mask.fill_diagonal_(0)
        
        # 计算对比损失
        exp_sim = torch.exp(sim_matrix)
        log_prob = sim_matrix - torch.log(exp_sim.sum(dim=1, keepdim=True))
        
        # 只考虑正样本对
        loss = -(log_prob * positive_mask).sum(dim=1) / positive_mask.sum(dim=1).clamp(min=1)
        
        return loss.mean()