from sklearn.ensemble import RandomForestClassifier  # 导入随机森林分类器
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

# 随机森林训练函数
def train_random_forest(train_data, y_train, params=None):
    """使用随机森林进行训练"""
    if params is None:
        # 设置与之前模型概念相似的参数
        params = {
            'n_estimators': 500,       # 树的数量
            'max_depth': 11,           # 树的最大深度
            'max_features': 'sqrt',    # 划分时考虑的最大特征数，'sqrt' 是一个常用选项
            'n_jobs': -1,              # 使用所有可用的CPU核心
            'random_state': 42         # 设置随机种子以保证结果可复现
        }

    # 初始化随机森林分类器
    model = RandomForestClassifier(**params)

    # 训练模型
    model.fit(train_data, y_train)

    # 预测训练集的概率，用于计算AUC
    # predict_proba 返回一个数组，其中第二列是类别为1的概率
    y_pred_proba = model.predict_proba(train_data)[:, 1]

    # 计算AUC
    auc_score = metrics.roc_auc_score(y_train, y_pred_proba)

    return model, auc_score

# 调用函数进行训练
rf_model, auc = train_random_forest(train_aligned, y_train)
print(f'AUC Score: {auc}')


# 预测测试集
yprob_rf = rf_model.predict_proba(test_aligned)[:, 1]

# 创建结果 DataFrame
result_rf = pd.DataFrame({
    'ID': test_all['Idx'],
    'Prediction': yprob_rf
    })

# 保存结果
result_rf.to_csv('result_rf.csv', encoding='utf-8', index=False)
print("随机森林预测结果已保存到 result_rf.csv")