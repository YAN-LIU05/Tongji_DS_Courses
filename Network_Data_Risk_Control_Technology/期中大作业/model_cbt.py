import pandas as pd
import numpy as np
import catboost as cbt
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import LabelEncoder
from sklearn import metrics

# --- 数据预处理函数 ---
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
    return train_df[common_cols].copy(), test_df[common_cols].copy()

# --- 读取和预处理数据 ---
print("正在读取和预处理数据...")
train_all = pd.read_csv('./train_all.csv', encoding='utf-8')
y_train_full = train_all.pop('target')
test_all = pd.read_csv('./test_all.csv', encoding='utf-8')

# 保留ID用于最后提交
test_ids = test_all['Idx']

train_aligned, test_aligned = align_features(train_all.drop('Idx', axis=1), test_all.drop('Idx', axis=1))
train_aligned = encode_categorical(train_aligned)
test_aligned = encode_categorical(test_aligned)

# --- 5折交叉验证CatBoost训练函数 ---
def train_cat_cv(train_data, y_train, test_data, n_splits=5):
    """使用5折交叉验证训练CatBoost模型"""
    params = {
        'objective': 'Logloss',
        'eval_metric': 'AUC',
        'iterations': 5000,
        'learning_rate': 0.02,
        'depth': 6,
        'random_seed': 42,
        'verbose': 0,
        'l2_leaf_reg': 3.0,
        'bootstrap_type': 'Bernoulli',
        'subsample': 0.8
    }
    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=2048)
    oof_preds = np.zeros(len(train_data))
    test_preds = np.zeros(len(test_data))

    print(f"\n开始 CatBoost {n_splits}-折 交叉验证...")
    for fold, (train_idx, val_idx) in enumerate(skf.split(train_data, y_train)):
        print(f"--- Fold {fold+1} ---")
        x_train, y_train_fold = train_data.iloc[train_idx], y_train.iloc[train_idx]
        x_val, y_val_fold = train_data.iloc[val_idx], y_train.iloc[val_idx]
        
        model = cbt.CatBoostClassifier(**params)
        model.fit(x_train, y_train_fold,
                  eval_set=[(x_val, y_val_fold)],
                  early_stopping_rounds=100,
                  use_best_model=True,
                  verbose=False) # 在fit内部关闭日志，让外部print控制
                  
        oof_preds[val_idx] = model.predict_proba(x_val)[:, 1]
        test_preds += model.predict_proba(test_data)[:, 1] / n_splits
        
    overall_oof_auc = metrics.roc_auc_score(y_train, oof_preds)
    return test_preds, overall_oof_auc

# --- 执行训练与预测 ---
final_predictions, cv_auc = train_cat_cv(train_aligned, y_train_full, test_aligned)
print(f'\n=============================================')
print(f'最终交叉验证 OOF AUC Score: {cv_auc:.6f}')
print(f'=============================================')

# --- 保存结果 ---
result_cat_cv = pd.DataFrame({
    'ID': test_ids,
    'Prediction': final_predictions
})
result_cat_cv.to_csv('result_catboost_cv.csv', encoding='utf-8', index=False)
print("5折CatBoost预测完成，结果已保存到 result_catboost_cv.csv")