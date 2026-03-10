import lightgbm as lgb
from sklearn import metrics
import pandas as pd
import numpy as np # 导入 numpy 用于计算平均值
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import StratifiedKFold # 导入交叉验证工具

def encode_categorical(df):
    """将object类型的列进行Label Encoding"""
    for col in df.columns:
        if df[col].dtype == 'object':
            le = LabelEncoder()
            df[col] = df[col].fillna('missing')
            df[col] = le.fit_transform(df[col])
    return df

# 读取数据
train_all = pd.read_csv('./train_all.csv', encoding='utf-8')
y_train_full = train_all.pop('target')
test_all = pd.read_csv('./test_all.csv', encoding='utf-8')

print(f"原始训练集形状: {train_all.shape}")
print(f"原始测试集形状: {test_all.shape}")

# 对齐特征
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

train_aligned, test_aligned = align_features(train_all, test_all)
train_aligned = encode_categorical(train_aligned)
test_aligned = encode_categorical(test_aligned)

# --- 优化的 LightGBM 交叉验证训练函数 ---
def train_lgb_cv(train_data, y_train, test_data, params=None, n_splits=5):
    """
    使用K折交叉验证和早停来训练LightGBM模型。
    """
    if params is None:
        # 提供一组更优化的初始参数
        params = {
            'objective': 'binary',
            'boosting_type': 'gbdt',
            'metric': 'auc', # 监控指标
            'num_leaves': 31,
            'learning_rate': 0.02,
            'feature_fraction': 0.8,
            'bagging_fraction': 0.8,
            'bagging_freq': 1,
            'lambda_l1': 0.1,
            'lambda_l2': 0.1,
            'verbose': -1,
            'n_jobs': -1,
            'seed': 42,
        }

    # 使用分层K折，确保每折中目标变量的比例相似
    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)

    # 初始化数组用于存储预测结果
    oof_preds = np.zeros(len(train_data)) # 存储对训练集的验证预测（Out-of-Fold）
    test_preds = np.zeros(len(test_data)) # 存储对测试集的预测

    print(f"开始 {n_splits}-折 交叉验证训练...")
    for fold, (train_idx, val_idx) in enumerate(skf.split(train_data, y_train)):
        print(f"--- 第 {fold+1} 折 ---")
        
        # 划分训练集和验证集
        x_train, y_train_fold = train_data.iloc[train_idx], y_train.iloc[train_idx]
        x_val, y_val_fold = train_data.iloc[val_idx], y_train.iloc[val_idx]

        # 创建LGB数据集
        lgb_train = lgb.Dataset(x_train, label=y_train_fold)
        lgb_val = lgb.Dataset(x_val, label=y_val_fold)

        # 训练模型，加入早停
        model = lgb.train(
            params,
            lgb_train,
            num_boost_round=5000,  # 设置一个较大的数，让早停来决定最佳迭代次数
            valid_sets=[lgb_train, lgb_val],
            valid_names=['train', 'valid'],
            callbacks=[lgb.early_stopping(stopping_rounds=100, verbose=True)] # 如果100轮内验证集auc没提升，就停止
        )

        # 预测验证集和测试集
        oof_preds[val_idx] = model.predict(x_val, num_iteration=model.best_iteration)
        test_preds += model.predict(test_data, num_iteration=model.best_iteration) / n_splits

    # 计算总体的OOF AUC分数
    overall_auc = metrics.roc_auc_score(y_train, oof_preds)
    
    return test_preds, overall_auc

# 调用新的交叉验证函数进行训练和预测
final_predictions, cv_auc = train_lgb_cv(train_aligned, y_train_full, test_aligned)
print(f'\n交叉验证 OOF AUC Score: {cv_auc}')

# 创建并保存结果文件
result_lgb_cv = pd.DataFrame({
    'ID': test_all['Idx'],
    'Prediction': final_predictions
    })
result_lgb_cv.to_csv('result_lgb_cv.csv', encoding='utf-8', index=False)
print("优化的LightGBM预测结果已保存到 result_lgb_cv.csv")