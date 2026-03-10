import torch
import os
from datetime import datetime
import shutil
from torch_geometric.utils import degree
import numpy as np


def prepare_folder(name, model_name):
    model_dir = f'./model_files/{name}/{model_name}/'
   
    if os.path.exists(model_dir):
        shutil.rmtree(model_dir)
    os.makedirs(model_dir)
    return model_dir


def prepare_tune_folder(name, model_name):
    str_time = datetime.strftime(datetime.now(), '%Y%m%d_%H%M%S')
    tune_model_dir = f'./tune_results/{name}/{model_name}/{str_time}/'
   
    if os.path.exists(tune_model_dir):
        print(f'rm tune_model_dir {tune_model_dir}')
        shutil.rmtree(tune_model_dir)
    os.makedirs(tune_model_dir)
    print(f'make tune_model_dir {tune_model_dir}')
    return tune_model_dir


def save_preds_and_params(parameters, preds, model, file):
    save_dict = {'parameters':parameters, 'preds': preds, 'params': model.state_dict()
           , 'nparams': sum(p.numel() for p in model.parameters())}
    torch.save(save_dict, file)
    return


def add_graph_features(data):
    """添加节点的图结构特征"""
    # 获取边索引
    if hasattr(data, 'edge_index'):
        edge_index = data.edge_index
    else:
        edge_index = data.adj_t.to_torch_sparse_coo_tensor().indices()
    
    num_nodes = data.x.size(0)
    
    # 计算节点度数
    deg = degree(edge_index[0], num_nodes=num_nodes, dtype=torch.float)
    
    # 归一化度数特征
    deg_normalized = (deg - deg.mean()) / (deg.std() + 1e-5)
    
    # 计算log(degree + 1)
    log_deg = torch.log(deg + 1)
    log_deg_normalized = (log_deg - log_deg.mean()) / (log_deg.std() + 1e-5)
    
    # 拼接到原始特征
    new_features = torch.cat([
        data.x, 
        deg_normalized.unsqueeze(1),
        log_deg_normalized.unsqueeze(1)
    ], dim=1)
    
    data.x = new_features
    
    return data


class EarlyStopping:
    """Early stopping utility"""
    def __init__(self, patience=50, min_delta=0, verbose=True):
        self.patience = patience
        self.min_delta = min_delta
        self.verbose = verbose
        self.counter = 0
        self.best_loss = None
        self.early_stop = False
        self.best_epoch = 0
        
    def __call__(self, val_loss, epoch):
        if self.best_loss is None:
            self.best_loss = val_loss
            self.best_epoch = epoch
        elif val_loss > self.best_loss - self.min_delta:
            self.counter += 1
            if self.verbose:
                print(f'EarlyStopping counter: {self.counter} out of {self.patience}')
            if self.counter >= self.patience:
                self.early_stop = True
                if self.verbose:
                    print(f'Early stopping triggered at epoch {epoch}')
        else:
            self.best_loss = val_loss
            self.best_epoch = epoch
            self.counter = 0
        
        return self.early_stop


def ensemble_predict(models, data, device):
    """多个模型的预测结果取平均"""
    predictions = []
    
    for model in models:
        model.eval()
        with torch.no_grad():
            out = model(data.x, data.adj_t)
            pred = out.exp()
            predictions.append(pred)
    
    # 平均预测
    ensemble_pred = torch.stack(predictions).mean(dim=0)
    return ensemble_pred