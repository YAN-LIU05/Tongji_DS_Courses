import xgboost as xgb
from sklearn import metrics
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import StratifiedKFold

# 1. 数据预处理函数
def encode_categorical(df):
    """将object类型的列进行Label Encoding"""
    for col in df.columns:
        if df[col].dtype == 'object':
            le = LabelEncoder()
            df[col] = df[col].fillna('missing')
            df[col] = le.fit_transform(df[col])
    return df

def align_features(train_df, test_df):
    """确保训练集和测试集有相同的特征列"""
    common_cols = list(set(train_df.columns) & set(test_df.columns))
    common_cols.sort()
    
    print(f"共同特征数量: {len(common_cols)}")
    
    missing_in_test = set(train_df.columns) - set(test_df.columns)
    missing_in_train = set(test_df.columns) - set(train_df.columns)
    
    if missing_in_test:
        print(f"测试集中缺失的特征: {missing_in_test}")
    if missing_in_train:
        print(f"训练集中缺失的特征: {missing_in_train}")
    
    return train_df[common_cols].copy(), test_df[common_cols].copy()

# 2. 读取数据
print("正在读取数据...")
train_all = pd.read_csv('./train_all.csv', encoding='utf-8')
y_train_full = train_all.pop('target') # 提取标签
test_all = pd.read_csv('./test_all.csv', encoding='utf-8')

print(f"原始训练集形状: {train_all.shape}")
print(f"原始测试集形状: {test_all.shape}")

# 3. 对齐与编码
train_aligned, test_aligned = align_features(train_all, test_all)
train_aligned = encode_categorical(train_aligned)
test_aligned = encode_categorical(test_aligned)

# 4. 优化的 XGBoost 交叉验证训练函数
def train_xgb_cv(train_data, y_train, test_data, params=None, n_splits=5):
    """
    使用K折交叉验证和早停来训练XGBoost模型。
    已修复 best_ntree_limit 错误。
    """
    if params is None:
        params = {
            'objective': 'binary:logistic',
            'booster': 'gbtree',
            'eval_metric': 'auc',
            'eta': 0.02,            # 学习率
            'max_depth': 5,         # 树深
            'subsample': 0.8,       # 样本采样
            'colsample_bytree': 0.8,# 特征采样
            'alpha': 0.1,           # L1 正则
            'lambda': 0.1,          # L2 正则
            'seed': 42,
            'nthread': -1           # 使用所有CPU核心
        }

    # 分层K折交叉验证
    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)

    # 初始化存储预测结果的数组
    oof_preds = np.zeros(len(train_data))
    test_preds = np.zeros(len(test_data))
    
    # 转换测试集为DMatrix (只需转换一次)
    dtest = xgb.DMatrix(test_data)

    print(f"\n开始 {n_splits}-折 交叉验证训练...")
    
    for fold, (train_idx, val_idx) in enumerate(skf.split(train_data, y_train)):
        print(f"--- 第 {fold+1} 折 ---")
        
        # 划分数据
        x_train, y_train_fold = train_data.iloc[train_idx], y_train.iloc[train_idx]
        x_val, y_val_fold = train_data.iloc[val_idx], y_train.iloc[val_idx]

        # 创建 DMatrix
        dtrain = xgb.DMatrix(x_train, label=y_train_fold)
        dval = xgb.DMatrix(x_val, label=y_val_fold)
        
        # 监控列表
        watchlist = [(dtrain, 'train'), (dval, 'eval')]
        
        # 训练模型
        model = xgb.train(
            params,
            dtrain,
            num_boost_round=5000,       # 设大一点，靠早停控制
            evals=watchlist,
            early_stopping_rounds=100,  # 100轮不提升则停止
            verbose_eval=100            # 每100轮打印一次
        )

        # --- 修复部分开始 ---
        # 获取最佳迭代次数
        best_iteration = model.best_iteration
        
        # 使用 iteration_range 进行预测 (XGBoost 新版本标准写法)
        # 注意：iteration_range 是左闭右开区间，所以要 +1
        oof_preds[val_idx] = model.predict(dval, iteration_range=(0, best_iteration + 1))
        test_preds += model.predict(dtest, iteration_range=(0, best_iteration + 1)) / n_splits
        # --- 修复部分结束 ---

    # 计算验证集总体AUC
    overall_auc = metrics.roc_auc_score(y_train, oof_preds)
    
    return test_preds, overall_auc

# 5. 执行训练与预测
final_predictions, cv_auc = train_xgb_cv(train_aligned, y_train_full, test_aligned)

print(f'\n=============================================')
print(f'最终交叉验证 OOF AUC Score: {cv_auc}')
print(f'=============================================')

# 6. 保存结果
result_xgb_cv = pd.DataFrame({
    'ID': test_all['Idx'],
    'Prediction': final_predictions
    })
result_xgb_cv.to_csv('result_xgb_cv.csv', encoding='utf-8', index=False)
print("预测完成，结果已保存到 result_xgb_cv.csv")