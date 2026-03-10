import lightgbm as lgb
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

def train_lightgbm(train_data, y_train, params=None, num_boost_round=100):
    if params is None:
        params = {
            'objective': 'binary',
            'boosting_type': 'gbdt',
            'num_leaves': 40,
            'learning_rate': 0.02,
            'feature_fraction': 0.2,
            'max_depth':11,
            'reg_alpha':0.45,
            'reg_lambda':0.45,
            'n_estimators':500,
        }

    lgb_train = lgb.Dataset(train_data, label=y_train)
    model = lgb.train(params, lgb_train, num_boost_round=num_boost_round)

    # 预测概率
    y_pred = model.predict(train_data)

    # 计算AUC
    auc_score = metrics.roc_auc_score(y_train, y_pred)

    return model, auc_score

# 调用函数进行训练
lgbmodel, auc = train_lightgbm(train_aligned, y_train)
print(f'AUC Score: {auc}')


# lgbmodel.predict(test_aligned)


yprob_lgb = lgbmodel.predict(test_aligned)
result_lgb = pd.DataFrame({
    'ID': test_all['Idx'],
    'Prediction': yprob_lgb
    })
# result_lgb
result_lgb.to_csv('result_lgb.csv',encoding='utf-8')