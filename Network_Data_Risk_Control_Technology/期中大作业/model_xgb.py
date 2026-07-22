import xgboost as xgb  # 导入 xgboost
from sklearn import metrics
import pandas as pd
from sklearn.preprocessing import LabelEncoder

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
y_train = train_all.pop('target')
test_all = pd.read_csv('./test_all.csv', encoding='utf-8')

print(f"原始训练集形状: {train_all.shape}")
print(f"原始测试集形状: {test_all.shape}")

# 对齐特征
def align_features(train_df, test_df):
    """确保训练集和测试集有相同的特征列"""
    common_cols = list(set(train_df.columns) & set(test_df.columns))
    common_cols.sort()
    
    print(f"共同特征数量: {len(common_cols)}")
    
    # 检查缺失的特征
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

# XGBoost 训练函数
def train_xgboost(train_data, y_train, params=None, num_boost_round=100):
    """使用XGBoost进行训练"""
    if params is None:
        params = {
            'objective': 'binary:logistic',  # 二分类任务
            'booster': 'gbtree',
            'eta': 0.02,  # 学习率
            'max_depth': 11,
            'subsample': 0.8,
            'colsample_bytree': 0.8,
            'alpha': 0.45,  # L1 正则化
            'lambda': 0.45,  # L2 正则化
            'eval_metric': 'auc' # 评估指标
        }

    # XGBoost 使用 DMatrix 数据结构
    dtrain = xgb.DMatrix(train_data, label=y_train)
    model = xgb.train(params, dtrain, num_boost_round=num_boost_round)

    # 预测概率
    y_pred = model.predict(dtrain)

    # 计算AUC
    auc_score = metrics.roc_auc_score(y_train, y_pred)

    return model, auc_score

# 调用函数进行训练
xgbmodel, auc = train_xgboost(train_aligned, y_train, num_boost_round=500) # num_boost_round 对应 n_estimators
print(f'AUC Score: {auc}')


# 预测测试集
dtest = xgb.DMatrix(test_aligned)
yprob_xgb = xgbmodel.predict(dtest)

# 创建结果 DataFrame
result_xgb = pd.DataFrame({
    'ID': test_all['Idx'],
    'Prediction': yprob_xgb
    })

# 保存结果
result_xgb.to_csv('result_xgb.csv', encoding='utf-8', index=False)
print("XGBoost 预测结果已保存到 result_xgb.csv")