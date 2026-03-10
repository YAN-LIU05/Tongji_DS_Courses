import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re
## 加载微软雅黑中文字体
from matplotlib.font_manager import FontProperties
myfont = FontProperties(fname=r"./SIMHEI.TTF.ttf",size=12)



def encodingstr(s):
    # 检查是否为字符串类型
    if not isinstance(s, str):
        return s  # 如果不是字符串，直接返回原值
    regex = re.compile(r'.+市')
    if regex.search(s):
        s = s[:-1]
        return s
    else:
        return s
def encodingregion(s):
    # 检查是否为字符串类型
    if not isinstance(s, str):
        return s  # 如果不是字符串，直接返回原值
    special = ['内蒙古自治区', '宁夏回族自治区', '广西壮族自治区', '新疆维吾尔自治区','西藏自治区']
    ret = ['内蒙古', '宁夏', '广西', '新疆', '西藏']
    for i in range(len(special)):
        if s == special[i]:
            return ret[i]
    regex1 = re.compile(r'.+省')
    regex2 = re.compile(r'.+市')
    if regex1.search(s):
        s = s[:-1]
        return s
    elif regex2.search(s):
        s = s[:-1]
        return s
    else:
        return s

# 训练集路径
train_path = './data/train/'
train_master = pd.read_csv(os.path.join(train_path, 'Master_Training_Set.csv'), encoding='gbk')
train_userupdateinfo = pd.read_csv(os.path.join(train_path, 'Userupdate_Info_Training_Set.csv'), encoding='gbk')
train_loginfo = pd.read_csv(os.path.join(train_path, 'LogInfo_Training_Set.csv'), encoding='gbk')
# 测试集路径
test_path = './data/test/'
test_master = pd.read_csv(os.path.join(test_path, 'Master_Test_Set.csv'), encoding='gbk')
test_userupdateinfo = pd.read_csv(os.path.join(test_path, 'Userupdate_Info_Test_Set.csv'), encoding='gbk')
test_loginfo = pd.read_csv(os.path.join(test_path, 'LogInfo_Test_Set.csv'), encoding='gbk')

# 查看训练集主表缺失值比例
n_null_rate = train_master.isnull().sum().sort_values(ascending=False)/30000
## 去掉缺失比例接近百分之百的字段
train_master.drop(['WeblogInfo_1' ,'WeblogInfo_3'],axis=1,inplace=True)
# 测试集
test_master.drop(['WeblogInfo_1' ,'WeblogInfo_3'],axis=1,inplace=True)

''' 数值填充'''
# 对数据集中的 UserInfo_12字段中的缺失值（NaN）进行填充，填充值为 2.0
train_master.loc[(train_master.UserInfo_12.isnull() , 'UserInfo_12')] = 2.0
test_master.loc[(test_master.UserInfo_12.isnull() , 'UserInfo_12')] = 2.0
# 对数据集中的 UserInfo_11字段中的缺失值（NaN）进行填充，填充值为 2.0
train_master.loc[(train_master.UserInfo_11.isnull() , 'UserInfo_11')] = 2.0
test_master.loc[(test_master.UserInfo_11.isnull() , 'UserInfo_11')] = 2.0
# 对数据集中的 UserInfo_13字段中的缺失值（NaN）进行填充，填充值为 2.0
train_master.loc[(train_master.UserInfo_13.isnull() , 'UserInfo_13')] = 2.0
test_master.loc[(test_master.UserInfo_13.isnull() , 'UserInfo_13')] = 2.0
# 对数据集中的 WeblogInfo_20字段中的缺失值（NaN）进行填充，填充值为 '不详'
train_master.loc[(train_master.WeblogInfo_20.isnull() , 'WeblogInfo_20')] = u'不详'
test_master.loc[(test_master.WeblogInfo_20.isnull() , 'WeblogInfo_20')] = u'不详'
# 对数据集中的 WeblogInfo_19字段中的缺失值（NaN）进行填充，填充值为 '不详'
train_master.loc[(train_master.WeblogInfo_19.isnull() , 'WeblogInfo_19')] = u'不详'
test_master.loc[(test_master.WeblogInfo_19.isnull() , 'WeblogInfo_19')] = u'不详'
# 对数据集中的 WeblogInfo_21字段中的缺失值（NaN）进行填充，填充值为 '0'
train_master.loc[(train_master.WeblogInfo_21.isnull() , 'WeblogInfo_21')] = '0'
test_master.loc[(test_master.WeblogInfo_21.isnull() , 'WeblogInfo_21')] = '0'


## 用众数填充缺失值
categoric_cols = ['UserInfo_1' ,'UserInfo_2' ,'UserInfo_3' ,'UserInfo_4' , 'UserInfo_5' ,'UserInfo_6','UserInfo_7','UserInfo_8','UserInfo_9','UserInfo_11','UserInfo_12','UserInfo_13','UserInfo_14','UserInfo_15','UserInfo_16','UserInfo_17','UserInfo_19','UserInfo_20','UserInfo_21','UserInfo_22','UserInfo_23','UserInfo_24','Education_Info1','Education_Info2','Education_Info3','Education_Info4','Education_Info5','Education_Info6','Education_Info7','Education_Info8','WeblogInfo_19','WeblogInfo_20','WeblogInfo_21','SocialNetwork_1','SocialNetwork_2','SocialNetwork_7','SocialNetwork_12']
for col in categoric_cols:
    # 训练集
    mode_cols = train_master[col].mode()[0]
    train_master.loc[(train_master[col].isnull() , col)] = mode_cols 
    # 测试集
    mode_cols_test = test_master[col].mode()[0]
    test_master.loc[(test_master[col].isnull() , col)] = mode_cols_test 
    
## 用均值填充缺失值 
numeric_cols = []
for col in train_master.columns:
    if col not in categoric_cols and col !=u'Idx' and col != 'target' and col !='ListingInfo':
        numeric_cols.append(col)  # 剩下的就是数值变量
        # 训练集
        mean_cols = train_master[col].mean()
        train_master.loc[(train_master[col].isnull() , col)] = mean_cols   
        # 测试集
        mean_cols_test = test_master[col].mean()
        test_master.loc[(test_master[col].isnull() , col)] = mean_cols_test   
  
y_train = train_master['target'].values


## 剔除标准差几乎为零的特征项
numeric_cols_for_std = [col for col in numeric_cols if col not in ['Idx', 'target', 'ListingInfo']]
feature_std = train_master[numeric_cols_for_std].std().sort_values(ascending=True)
# 设定标准差阈值
threshold = 0.001
# 找出标准差小于阈值的特征
features_to_drop = feature_std[feature_std < threshold].index
# 训练集
train_master.drop(features_to_drop, axis=1, inplace=True)
train_master['Idx'] = train_master['Idx'].astype(np.int32)
# 测试集
test_master.drop(features_to_drop, axis=1, inplace=True)
test_master['Idx'] = test_master['Idx'].astype(np.int32)


# 去掉空格
train_master['UserInfo_9'] = train_master['UserInfo_9'].apply(lambda x: x.strip())
test_master['UserInfo_9'] = test_master['UserInfo_9'].apply(lambda x: x.strip())# 测试集
## 去掉大小写
train_userupdateinfo['UserupdateInfo1'] = train_userupdateinfo['UserupdateInfo1'].apply(lambda x:x.lower())
test_userupdateinfo['UserupdateInfo1'] = test_userupdateinfo['UserupdateInfo1'].apply(lambda x:x.lower())
## 将UserInfo中城市名归一化
train_master['UserInfo_2'] = train_master['UserInfo_2'].apply(lambda x: encodingstr(x))
train_master['UserInfo_4'] = train_master['UserInfo_4'].apply(lambda x: encodingstr(x))
train_master['UserInfo_7'] = train_master['UserInfo_7'].apply(lambda x: encodingregion(x))
train_master['UserInfo_19'] = train_master['UserInfo_19'].apply(lambda x: encodingregion(x))
train_master['UserInfo_8'] = train_master['UserInfo_8'].apply(lambda x: encodingstr(x))
train_master['UserInfo_20'] = train_master['UserInfo_20'].apply(lambda x: encodingstr(x))
# 测试集
test_master['UserInfo_2'] = test_master['UserInfo_2'].apply(lambda x: encodingstr(x))
test_master['UserInfo_4'] = test_master['UserInfo_4'].apply(lambda x: encodingstr(x))
test_master['UserInfo_7'] = test_master['UserInfo_7'].apply(lambda x: encodingregion(x))
test_master['UserInfo_19'] = test_master['UserInfo_19'].apply(lambda x: encodingregion(x))
test_master['UserInfo_8'] = test_master['UserInfo_8'].apply(lambda x: encodingstr(x))
test_master['UserInfo_20'] = test_master['UserInfo_20'].apply(lambda x: encodingstr(x))


'''删除离群点'''
std_threshold = 3  # 阈值为均值的3倍标准差
for col in numeric_cols:
    if col in train_master.columns:  # 添加列存在性检查
        mean = train_master[col].mean()
        std = train_master[col].std()
        # 识别离群点
        outliers = train_master[abs(train_master[col] - mean) > std_threshold * std]
        # 用均值替换离群点
        train_master.loc[abs(train_master[col] - mean) > std_threshold * std, col] = mean

        # 测试集
        mean_test = test_master[col].mean()
        std_test = test_master[col].std()
        outliers = test_master[abs(test_master[col] - mean_test) > std_threshold * std_test]
        test_master.loc[abs(test_master[col] - mean_test) > std_threshold * std_test, col] = mean_test


# 保存清洗后的数据
train_userupdateinfo.to_csv('./train_userupdateinfo.csv', index=False, encoding='utf-8')
test_userupdateinfo.to_csv('./test_userupdateinfo.csv', index=False, encoding='utf-8')


## 借款日期离散化
# 把月、日、单独拎出来，放到3列中
train_master['month'] = pd.DatetimeIndex(train_master.ListingInfo).month
train_master['day']  = pd.DatetimeIndex(train_master.ListingInfo).day
train_master['day'].head()
train_master.drop(['ListingInfo'],axis=1,inplace=True)
train_master['target'] = train_master['target'].astype(str)
train_master.to_csv('./train_master.csv',index=False,encoding='utf-8')

# 测试集
test_master['month'] = pd.DatetimeIndex(test_master.ListingInfo).month
test_master['day']  = pd.DatetimeIndex(test_master.ListingInfo).day
test_master['day'].head()
test_master.drop(['ListingInfo'],axis=1,inplace=True)
test_master.to_csv('./test_master.csv',index=False,encoding='utf-8')