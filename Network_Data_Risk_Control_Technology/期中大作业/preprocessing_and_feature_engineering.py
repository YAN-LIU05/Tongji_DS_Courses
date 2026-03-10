import os
import pandas as pd
import numpy as np

def get_city_level(city):
    first_level = ['北京', '上海', '广州', '深圳']
    new_first_level = ['成都', '重庆', '杭州', '武汉', '西安', '郑州', '青岛', '长沙', '天津', '苏州', '南京', '东莞',
                      '沈阳', '合肥', '佛山']
    second_level = ['昆明', '福州', '无锡', '厦门', '哈尔滨', '长春', '南昌', '济南', '宁波', '大连', '贵阳', '温州',
                   '石家庄', '泉州', '南宁', '金华', '常州', '珠海', '惠州', '嘉兴', '南通', '中山', '保定', '兰州',
                   '台州', '徐州', '太原', '绍兴', '烟台', '廊坊']
    third_level = ['海口', '汕头', '潍坛', '扬州', '洛阳', '乌鲁木齐', '临沂', '唐山', '镇江', '盐城', '湖州', '赣州',
                  '漳州', '揭阳', '江门', '桂林', '邯郸', '泰州', '济宁', '呼和浩特', '咸阳', '芜湖', '三亚', '阜阳',
                  '淮安', '遵义', '银川', '衡阳', '上饶', '柳州', '淄博', '莆田', '绵阳', '湛江', '商丘', '宜昌',
                  '沧州', '连云港', '南阳', '蚌埠', '驻马店', '滁州', '邢台', '潮州', '秦皇岛', '肇庆', '荆州', '周口',
                  '马鞍山', '清远', '宿州', '威海', '九江', '新乡', '信阳', '襄阳', '岳阳', '安庆', '菏泽', '宜春',
                  '黄冈', '泰安', '宿迁', '株洲', '宁德', '鞍山', '南充', '六安', '大庆', '舟山']
    fourth_level = ['常德', '渭南', '孝感', '丽水', '运城', '德州', '张家口', '鄂尔多斯', '阳江', '泸州', '丹东', '曲靖',
                   '乐山', '许昌', '湘潭', '晋中', '安阳', '齐齐哈尔', '北海', '宝鸡', '抚州', '景德镇', '延安', '三明',
                   '抚顺', '亳州', '日照', '西宁', '衢州', '拉萨', '淮北', '焦作', '平顶山', '滨州', '吉安', '濮阳',
                   '眉山', '池州', '荆门', '铜仁', '长治', '衡水', '铜陵', '承德', '达州', '邵阳', '德阳', '龙岩',
                   '南平', '淮南', '黄石', '营口', '东营', '吉林', '韶关', '枣庄', '包头', '怀化', '宣城', '临汾',
                   '聊城', '梅州', '盘锦', '锦州', '榆林', '玉林', '十堰', '汕尾', '咸宁', '宜宾', '永州', '益阳',
                   '黔南州', '黔东南', '恩施', '红河', '大理', '大同', '鄂州', '忻州', '吕梁', '黄山', '开封', '郴州',
                   '茂名', '漯河', '葫芦岛', '河源', '娄底', '延边']

    if city in first_level:
        return 1
    elif city in new_first_level:
        return 2
    elif city in second_level:
        return 3
    elif city in third_level:
        return 4
    elif city in fourth_level:
        return 5
    elif city == '不详':
        return 6
    return None

# 训练集路径
train_master = pd.read_csv('./train_master.csv')
test_master = pd.read_csv('./test_master.csv')

city_col = ['UserInfo_2', 'UserInfo_4', 'UserInfo_8', 'UserInfo_20']
for col in city_col:
    train_master[col] = train_master[col].apply(get_city_level)
    mode_value = train_master[col].mode()[0]# 众数填充
    train_master[col].fillna(mode_value, inplace=True)
    # print(master[col].head(5))
    # 测试集
    test_master[col] = test_master[col].apply(get_city_level)
    mode_value = test_master[col].mode()[0]
    test_master[col].fillna(mode_value, inplace=True)


from collections import defaultdict
import datetime as dt

##  userupdateinfo表
userupdate_info_number = defaultdict(list)  ### 用户信息更新的次数
userupdate_info_category = defaultdict(set)  ###用户信息更新的种类数
userupdate_info_times = defaultdict(list)  ### 用户分几次更新了
userupdate_info_date = defaultdict(list)  #### 用户借款成交与信息更新时间跨度

with open('./train_userupdateinfo.csv', 'r') as f:
    f.readline()
    for line in f.readlines():
        cols = line.strip().split(",")  ### cols 是list结果
        userupdate_info_date[cols[0]].append(cols[1])
        userupdate_info_number[cols[0]].append(cols[2])
        userupdate_info_category[cols[0]].add(cols[2])
        userupdate_info_times[cols[0]].append(cols[3])
    print(u'提取信息完成')

userupdate_info_number_ = defaultdict(int)  ### 用户信息更新的次数
userupdate_info_category_ = defaultdict(int)  ### 用户信息更新的种类数
userupdate_info_times_ = defaultdict(int)  ### 用户分几次更新了
userupdate_info_date_ = defaultdict(int)  #### 用户借款成交与信息更新时间跨度


for key in userupdate_info_date.keys():
    userupdate_info_times_[key] = len(set(userupdate_info_times[key]))
    delta_date = dt.datetime.strptime(userupdate_info_date[key][0], '%Y/%m/%d') - dt.datetime.strptime(
        list(set(userupdate_info_times[key]))[0], '%Y/%m/%d')
    userupdate_info_date_[key] = abs(delta_date.days)
    userupdate_info_number_[key] = len(userupdate_info_number[key])
    userupdate_info_category_[key] = len(userupdate_info_category[key])

print('信息处理完成')


## 建立一个DataFrame
Idx_ = list(userupdate_info_date_.keys())  #### list
numbers_ = list(userupdate_info_number_.values())
categorys_ = list(userupdate_info_category_.values())
times_ = list(userupdate_info_times_.values())
dates_ = list(userupdate_info_date_.values())
userupdate_df = pd.DataFrame(
    {'Idx': Idx_, 'numbers': numbers_, 'categorys': categorys_, 'times': times_, 'dates': dates_})
userupdate_df.head()
userupdate_df.to_csv('./userupdate_df.csv', index=False, encoding='utf-8')


userupdate_info_number = defaultdict(list) ### 用户信息更新的次数
userupdate_info_category = defaultdict(set) ###用户信息更新的种类数
userupdate_info_times = defaultdict(list) ### 用户分几次更新了
userupdate_info_date = defaultdict(list) #### 用户借款成交与信息更新时间跨度

with open('./test_userupdateinfo.csv' ,'r') as f:
    f.readline()
    for line in f.readlines():
        cols = line.strip().split(",") ### cols 是list结果
        userupdate_info_date[cols[0]].append(cols[1])
        userupdate_info_number[cols[0]].append(cols[2])
        userupdate_info_category[cols[0]].add(cols[2])
        userupdate_info_times[cols[0]].append(cols[3])
    print(u'提取信息完成')

userupdate_info_number_ = defaultdict(int) ### 用户信息更新的次数
userupdate_info_category_ = defaultdict(int) ### 用户信息更新的种类数
userupdate_info_times_ = defaultdict(int) ### 用户分几次更新了
userupdate_info_date_ = defaultdict(int) #### 用户借款成交与信息更新时间跨度

for key in userupdate_info_date.keys():
    userupdate_info_times_[key] = len(set(userupdate_info_times[key]))
    delta_date = dt.datetime.strptime(userupdate_info_date[key][0] ,'%Y/%m/%d') - dt.datetime.strptime(list(set(userupdate_info_times[key]))[0] ,'%Y/%m/%d')
    userupdate_info_date_[key] = abs(delta_date.days)
    userupdate_info_number_[key] = len(userupdate_info_number[key])
    userupdate_info_category_[key] = len(userupdate_info_category[key])

print('信息处理完成')

## 建立一个DataFrame
Idx_ = list(userupdate_info_date_.keys()) #### list
numbers_ = list(userupdate_info_number_.values())
categorys_ = list(userupdate_info_category_.values())
times_ = list(userupdate_info_times_.values())
dates_ = list(userupdate_info_date_.values())
userupdate_df = pd.DataFrame({'Idx':Idx_ , 'numbers':numbers_ ,'categorys':categorys_ ,'times':times_ ,'dates':dates_ })
userupdate_df.head()
userupdate_df.to_csv('./userupdate_df_test.csv',index=False,encoding='utf-8')