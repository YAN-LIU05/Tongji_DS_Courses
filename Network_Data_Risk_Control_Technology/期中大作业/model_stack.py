import pandas as pd
import numpy as np
import lightgbm as lgb
import xgboost as xgb
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import LabelEncoder
from sklearn.linear_model import LogisticRegression  # 导入逻辑回归作为元模型
from sklearn import metrics

# --- 1. 数据预处理函数 (与之前相同) ---
def encode_categorical(df):
    for col in df.columns:
        if df[col].dtype == 'object':
            le = LabelEncoder()
            df[col] = df[col].fillna('missing')
            df[col] = le.fit_transform(df[col])
    return df

def align_features(train_df, test_df):
    common_cols = list(set(train_df.columns) & set(test_df.columns))
    common_cols.sort()
    return train_df[common_cols].copy(), test_df[common_cols].copy()

# --- 2. 优化的基模型训练函数 (修改后返回OOF和测试预测) ---

def train_lgb_cv(train_data, y_train, test_data, n_splits=5):
    """训练LightGBM并返回OOF和测试集预测"""
    params = {
        'objective': 'binary', 'metric': 'auc', 'boosting_type': 'gbdt',
        'num_leaves': 31, 'learning_rate': 0.02, 'feature_fraction': 0.8,
        'bagging_fraction': 0.8, 'bagging_freq': 1, 'lambda_l1': 0.1,
        'lambda_l2': 0.1, 'verbose': -1, 'n_jobs': -1, 'seed': 42,
    }
    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)
    oof_preds = np.zeros(len(train_data))
    test_preds = np.zeros(len(test_data))

    print(f"开始 LightGBM {n_splits}-折 交叉验证...")
    for fold, (train_idx, val_idx) in enumerate(skf.split(train_data, y_train)):
        print(f"--- LGB Fold {fold+1} ---")
        x_train, y_train_fold = train_data.iloc[train_idx], y_train.iloc[train_idx]
        x_val, y_val_fold = train_data.iloc[val_idx], y_train.iloc[val_idx]
        lgb_train = lgb.Dataset(x_train, label=y_train_fold)
        lgb_val = lgb.Dataset(x_val, label=y_val_fold)
        model = lgb.train(
            params, lgb_train, num_boost_round=5000, valid_sets=[lgb_val],
            callbacks=[lgb.early_stopping(100, verbose=False)]
        )
        oof_preds[val_idx] = model.predict(x_val, num_iteration=model.best_iteration)
        test_preds += model.predict(test_data, num_iteration=model.best_iteration) / n_splits
    return oof_preds, test_preds

def train_xgb_cv(train_data, y_train, test_data, n_splits=5):
    """训练XGBoost并返回OOF和测试集预测"""
    params = {
        'objective': 'binary:logistic', 'eval_metric': 'auc', 'booster': 'gbtree',
        'eta': 0.02, 'max_depth': 5, 'subsample': 0.8, 'colsample_bytree': 0.8,
        'alpha': 0.1, 'lambda': 0.1, 'seed': 42, 'nthread': -1
    }
    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)
    oof_preds = np.zeros(len(train_data))
    test_preds = np.zeros(len(test_data))
    dtest = xgb.DMatrix(test_data)

    print(f"\n开始 XGBoost {n_splits}-折 交叉验证...")
    for fold, (train_idx, val_idx) in enumerate(skf.split(train_data, y_train)):
        print(f"--- XGB Fold {fold+1} ---")
        x_train, y_train_fold = train_data.iloc[train_idx], y_train.iloc[train_idx]
        x_val, y_val_fold = train_data.iloc[val_idx], y_train.iloc[val_idx]
        dtrain = xgb.DMatrix(x_train, label=y_train_fold)
        dval = xgb.DMatrix(x_val, label=y_val_fold)
        watchlist = [(dtrain, 'train'), (dval, 'eval')]
        model = xgb.train(
            params, dtrain, num_boost_round=5000,
            evals=watchlist, early_stopping_rounds=100, verbose_eval=False
        )
        oof_preds[val_idx] = model.predict(dval, iteration_range=(0, model.best_iteration + 1))
        test_preds += model.predict(dtest, iteration_range=(0, model.best_iteration + 1)) / n_splits
    return oof_preds, test_preds

# --- 3. 主流程 ---
# 读取和预处理数据
print("正在读取和预处理数据...")
train_all = pd.read_csv('./train_all.csv', encoding='utf-8')
y_train_full = train_all.pop('target')
test_all = pd.read_csv('./test_all.csv', encoding='utf-8')

train_aligned, test_aligned = align_features(train_all, test_all)
train_aligned = encode_categorical(train_aligned)
test_aligned = encode_categorical(test_aligned)

# --- Level 0: 训练基模型并收集预测 ---
# 训练 LightGBM
oof_preds_lgb, test_preds_lgb = train_lgb_cv(train_aligned, y_train_full, test_aligned)
oof_auc_lgb = metrics.roc_auc_score(y_train_full, oof_preds_lgb)
print(f"\nLightGBM OOF AUC Score: {oof_auc_lgb}")

# 训练 XGBoost
oof_preds_xgb, test_preds_xgb = train_xgb_cv(train_aligned, y_train_full, test_aligned)
oof_auc_xgb = metrics.roc_auc_score(y_train_full, oof_preds_xgb)
print(f"XGBoost OOF AUC Score: {oof_auc_xgb}")

# --- Level 1: 训练元模型并进行最终预测 ---
print("\n--- 开始训练 Level 1 元模型 (Stacking) ---")

# 创建元模型的训练和测试特征
# np.column_stack 将两个一维数组按列合并成一个二维数组
meta_features_train = np.column_stack((oof_preds_lgb, oof_preds_xgb))
meta_features_test = np.column_stack((test_preds_lgb, test_preds_xgb))

# 初始化并训练元模型（逻辑回归）
# 逻辑回归非常适合作为元模型，因为它简单、快速，且能有效找到预测之间的线性关系
meta_model = LogisticRegression(penalty='l2', random_state=42)
meta_model.fit(meta_features_train, y_train_full)

# 打印元模型学习到的系数，可以了解它给每个基模型分配的权重
print(f"元模型学习到的系数 (权重): LGB={meta_model.coef_[0][0]:.4f}, XGB={meta_model.coef_[0][1]:.4f}")

# 使用元模型进行最终预测
final_stacked_preds = meta_model.predict_proba(meta_features_test)[:, 1]

# (可选) 简单平均融合作为对比
simple_avg_preds = (test_preds_lgb + test_preds_xgb) / 2

# --- 4. 保存结果 ---
result_stacking = pd.DataFrame({
    'ID': test_all['Idx'],
    'Prediction': final_stacked_preds
})
result_stacking.to_csv('result_stacking.csv', encoding='utf-8', index=False)
print("\nStacking 融合预测完成，结果已保存到 result_stacking.csv")