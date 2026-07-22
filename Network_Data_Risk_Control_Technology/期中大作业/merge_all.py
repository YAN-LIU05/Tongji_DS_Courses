import pandas as pd
import numpy as np
from matplotlib.pylab import rcParams
rcParams['figure.figsize'] = 12, 4
import os

train_path = './data/train/'
train_loginfo = pd.read_csv(os.path.join(train_path, 'LogInfo_Training_Set.csv'), encoding='gbk')
# 测试集路径
test_path = './data/test/'
test_loginfo = pd.read_csv(os.path.join(test_path, 'LogInfo_Test_Set.csv'), encoding='gbk')

#每个用户登录天数
def calculate_login_days(train_loginfo):
    # 将登录时间转换为 datetime 对象
    train_loginfo['LoginDate'] = pd.to_datetime(train_loginfo['LogInfo3'])
    
    # 计算每个用户的登录天数
    login_days = train_loginfo.groupby(['Idx'])['LoginDate'].nunique().reset_index(name='LoginDays')
    return login_days

#每个用户平均登录时间间隔
def calculate_average_login_interval(train_loginfo):
    # 将登录时间转换为 datetime 对象
    train_loginfo['LoginDate'] = pd.to_datetime(train_loginfo['LogInfo3'])
    
    # 计算每个用户的登录时间序列
    train_loginfo_sorted = train_loginfo.sort_values(by=['Idx', 'LoginDate']).reset_index(drop=True)
    
    # 计算相邻登录时间的间隔
    train_loginfo_sorted['NextLoginDate'] = train_loginfo_sorted.groupby(['Idx'])['LoginDate'].shift(-1)
    train_loginfo_sorted['LoginInterval'] = (train_loginfo_sorted['NextLoginDate'] - train_loginfo_sorted['LoginDate']).dt.days
    
    # 计算平均登录间隔
    average_login_intervals = train_loginfo_sorted.groupby(['Idx'])['LoginInterval'].mean().reset_index(name='AverageLoginInterval')
    return average_login_intervals

#每个用户每种操作代码次数
def count_operation_codes(train_loginfo):
    # 统计每种操作代码的次数
    operation_counts = train_loginfo.groupby(['Idx', 'LogInfo1']).size().unstack(fill_value=0).reset_index()
    operation_counts.columns = ['Idx'] + ['OpCount_' + str(col) for col in operation_counts.columns[1:]]
    return operation_counts


# 登录天数
login_days = calculate_login_days(train_loginfo)
# 平均登录时间间隔
average_login_intervals = calculate_average_login_interval(train_loginfo)
# 每个用户操作代码的种类数
operation_counts = count_operation_codes(train_loginfo)
# 每个用户登录天数
login_days_test = calculate_login_days(test_loginfo)
# 每个用户平均登录时间间隔
average_login_intervals_test = calculate_average_login_interval(test_loginfo)
# 每个用户每种操作代码次数
operation_counts_test = count_operation_codes(test_loginfo)

# 获取两个表的属性名
columns_df1 = set(operation_counts.columns)
columns_df2 = set(operation_counts_test.columns)

# 计算交集
common_columns = columns_df1.intersection(columns_df2)

# 删除不在交集的特征
columns_to_drop = [col for col in operation_counts.columns if col not in common_columns]
operation_counts = operation_counts.drop(columns=columns_to_drop)
columns_to_drop = [col for col in operation_counts_test.columns if col not in common_columns]
operation_counts_test = operation_counts_test.drop(columns=columns_to_drop)



# 合并所有特征
loginfo_df = pd.merge(login_days, average_login_intervals, on='Idx', how='outer')
loginfo_df = pd.merge(loginfo_df, operation_counts, on='Idx', how='outer')
loginfo_df.to_csv('./loginfo_df.csv',index=False,encoding='utf-8')
# 测试集
loginfo_df_test = pd.merge(login_days_test, average_login_intervals_test, on='Idx', how='outer')
loginfo_df_test = pd.merge(loginfo_df_test, operation_counts_test, on='Idx', how='outer')
loginfo_df_test.to_csv('./loginfo_df_test.csv',index=False,encoding='utf-8')

# 训练集
train_master = pd.read_csv('./train_master.csv',encoding='utf-8')
train_userupdateinfo = pd.read_csv('./userupdate_df.csv',encoding='utf-8')
train_loginfo = pd.read_csv('./loginfo_df.csv',encoding='utf-8')
# 测试集
test_master = pd.read_csv('./test_master.csv',encoding='utf-8')
test_userupdateinfo = pd.read_csv('./userupdate_df_test.csv',encoding='utf-8')
test_loginfo = pd.read_csv('./loginfo_df_test.csv',encoding='utf-8')

# 合并所有特征
# 训练集
train_all = pd.merge(train_master, train_userupdateinfo, how='left', on='Idx')
train_all = pd.merge(train_all, train_loginfo, how='left', on='Idx')
# 测试集
test_all = pd.merge(test_master, test_userupdateinfo, how='left', on='Idx')
test_all = pd.merge(test_all, test_loginfo, how='left', on='Idx')


## 填充缺失值
# 填充 AverageLoginInterval（数值型变量）
train_all['AverageLoginInterval'].fillna(train_all['AverageLoginInterval'].mean(), inplace=True)
test_all['AverageLoginInterval'].fillna(test_all['AverageLoginInterval'].mean(), inplace=True)

# 填充 OpCount_x 列（类别型变量）
op_count_columns = [
    'OpCount_3001', 'OpCount_5', 'OpCount_22', 'OpCount_12', 'OpCount_11', 
    'OpCount_10', 'OpCount_9', 'OpCount_8', 'OpCount_6', 'OpCount_4', 
    'OpCount_100', 'OpCount_3', 'OpCount_2', 'OpCount_0', 'OpCount_-4', 
    'OpCount_-10', 'OpCount_99', 'OpCount_1', 'OpCount_101', 'OpCount_303', 
    'OpCount_102', 'OpCount_3000', 'OpCount_1000', 'OpCount_310', 'OpCount_307', 
    'OpCount_305', 'OpCount_304', 'OpCount_2000', 'OpCount_302', 'OpCount_103', 
    'OpCount_207', 'OpCount_107', 'OpCount_300', 'OpCount_104'
]


for col in op_count_columns:
    train_all[col].fillna(train_all[col].mode()[0], inplace=True)
    test_all[col].fillna(test_all[col].mode()[0], inplace=True)

# 填充 LoginDays（类别型变量）
train_all['LoginDays'].fillna(0, inplace=True)
test_all['LoginDays'].fillna(0, inplace=True)

# 填充 times, categorys, numbers, dates（类别型变量）
train_all['times'].fillna(0, inplace=True)
train_all['categorys'].fillna(0, inplace=True)
train_all['numbers'].fillna(0, inplace=True)
train_all['dates'].fillna(0, inplace=True)

test_all['times'].fillna(0, inplace=True)
test_all['categorys'].fillna(0, inplace=True)
test_all['numbers'].fillna(0, inplace=True)
test_all['dates'].fillna(0, inplace=True)

## 对数值型特征进行scaling
import warnings
from sklearn.preprocessing import StandardScaler, MinMaxScaler
warnings.filterwarnings("ignore")
# 所有分类特征
var_info = pd.read_csv('./data/var_info.csv')
# 确定特征类型列的名称
feature_type_column = '变量类型'
feature_column = '变量名称'
# 筛选出 feature_type 为 "Categorical" 的特征
categorical_features = var_info[var_info[feature_type_column] == 'Categorical'][feature_column]


# 获取 DataFrameA 的属性名
columns_train_all = set(train_all.columns)

# 过滤 categorical_features
filtered_categorical_features = [feat for feat in categorical_features if feat in columns_train_all]


columns_train_all = train_all.columns.tolist()
# 选择索引247到282属性名
start_index = 247  
end_index = 282
additional_categorical_features = columns_train_all[start_index:end_index]
# 合并属性名列表
filtered_categorical_features.extend(additional_categorical_features)


# 选择索引216到240属性名
start_index = 216  
end_index = 240
additional_categorical_features = columns_train_all[start_index:end_index]
# 合并属性名列表
filtered_categorical_features.extend(additional_categorical_features)
additional_categorical_features = columns_train_all[0:1]
filtered_categorical_features.extend(additional_categorical_features)


numeric_features = [col for col in columns_train_all if col not in filtered_categorical_features]
# 对数值型特征应用 StandardScaler标准化
scaler = StandardScaler()
train_all[numeric_features] = scaler.fit_transform(train_all[numeric_features])


# 获取 DataFrameA 的属性名
columns_test_all = set(test_all.columns)

# 过滤 categorical_features
filtered_categorical_features = [feat for feat in categorical_features if feat in columns_test_all]

columns_test_all = test_all.columns.tolist()
# 选择索引247到282属性名
start_index = 247  
end_index = 282
additional_categorical_features = columns_test_all[start_index:end_index]
# 合并属性名列表
filtered_categorical_features.extend(additional_categorical_features)

# 选择索引216到240属性名
start_index = 216  
end_index = 240
additional_categorical_features = columns_test_all[start_index:end_index]
# 合并属性名列表
filtered_categorical_features.extend(additional_categorical_features)
additional_categorical_features = columns_test_all[0:1]
filtered_categorical_features.extend(additional_categorical_features)

numeric_features = [col for col in columns_test_all if col not in filtered_categorical_features]
# 对数值型特征应用 StandardScaler标准化
#scaler = StandardScaler()
test_all[numeric_features] = scaler.fit_transform(test_all[numeric_features])


train_all['Idx'] = train_all['Idx'].astype(np.int64)
train_all['target'] = train_all['target'].astype(np.int64)
# train_all = pd.get_dummies(train_all)
train_all.to_csv('./train_all.csv',encoding='utf-8',index=False)
y_train = train_all.pop('target')


test_all['Idx'] = test_all['Idx'].astype(np.int64)
# test_all = pd.get_dummies(test_all)
# test_all.head()
test_all.to_csv('./test_all.csv',encoding='utf-8',index=False)