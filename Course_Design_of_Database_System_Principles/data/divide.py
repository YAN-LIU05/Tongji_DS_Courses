import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# 读取原始数据
print("正在读取原始数据...")
df = pd.read_csv('data.csv')
print(f"原始数据共 {len(df)} 条记录")

# ==================== 1. PoiMaster（文旅资源主表） ====================
print("\n处理 PoiMaster 表...")
poi_master = df[['poi_id', 'poi_name', 'poi_type', 'address', 'longitude', 'latitude', 'description']].copy()
poi_master = poi_master.drop_duplicates(subset=['poi_id'])
poi_master = poi_master.sort_values('poi_id')

poi_master.to_csv('PoiMaster.csv', index=False, encoding='utf-8-sig')
print(f"✓ PoiMaster: {len(poi_master)} 条记录")

# ==================== 2. ScenicSpotDetails（景区扩展） ====================
print("\n处理 ScenicSpotDetails 表...")
# 只选择景区类型且有scenic_level数据的记录
scenic_details = df[(df['poi_type'] == 'scenic_spot') & (df['scenic_level'].notna())][
    ['poi_id', 'scenic_level', 'max_capacity']].copy()
scenic_details = scenic_details.drop_duplicates(subset=['poi_id'])

scenic_details_output = pd.DataFrame({
    's_id': range(1, len(scenic_details) + 1),
    'scenic_spot_id': scenic_details['poi_id'].values,
    'level': scenic_details['scenic_level'].values,
    'max_capacity': scenic_details['max_capacity'].values
})

scenic_details_output.to_csv('ScenicSpotDetails.csv', index=False, encoding='utf-8-sig')
print(f"✓ ScenicSpotDetails: {len(scenic_details_output)} 条记录")

# ==================== 3. HotelDetails（酒店扩展） ====================
print("\n处理 HotelDetails 表...")
# 只选择酒店类型且有star_rating数据的记录
hotel_details = df[(df['poi_type'] == 'hotel') & (df['star_rating'].notna())][
    ['poi_id', 'star_rating', 'room_count']].copy()
hotel_details = hotel_details.drop_duplicates(subset=['poi_id'])

hotel_details_output = pd.DataFrame({
    'h_id': range(1, len(hotel_details) + 1),
    'hotel_id': hotel_details['poi_id'].values,
    'scenic_spot_detail_id': np.nan,  # 可后续关联
    'star_rating': hotel_details['star_rating'].values,
    'room_count': hotel_details['room_count'].values
})

hotel_details_output.to_csv('HotelDetails.csv', index=False, encoding='utf-8-sig')
print(f"✓ HotelDetails: {len(hotel_details_output)} 条记录")

# ==================== 4. EnterpriseInfo（企业信息表） ====================
print("\n处理 EnterpriseInfo 表...")
# 提取唯一的企业信息
enterprise_raw = df[['enterprise_id', 'enterprise_name', 'enterprise_type']].copy()
enterprise_raw = enterprise_raw.dropna(subset=['enterprise_id'])
enterprise_raw = enterprise_raw.drop_duplicates(subset=['enterprise_id'])
enterprise_raw = enterprise_raw.sort_values('enterprise_id')

# 确保enterprise_id是整数
enterprise_raw['enterprise_id'] = enterprise_raw['enterprise_id'].astype(int)

enterprise_info_output = enterprise_raw.copy()
enterprise_info_output.to_csv('EnterpriseInfo.csv', index=False, encoding='utf-8-sig')
print(f"✓ EnterpriseInfo: {len(enterprise_info_output)} 条记录")

# ==================== 5. EnterprisePoiLink（企业POI关联表） ====================
print("\n处理 EnterprisePoiLink 表...")
# 提取企业和POI的关联关系
enterprise_poi_link = df[['enterprise_id', 'poi_id', 'relationship_type']].copy()
enterprise_poi_link = enterprise_poi_link.dropna(subset=['enterprise_id', 'poi_id'])
enterprise_poi_link = enterprise_poi_link.drop_duplicates(subset=['enterprise_id', 'poi_id'])

# 确保ID是整数
enterprise_poi_link['enterprise_id'] = enterprise_poi_link['enterprise_id'].astype(int)
enterprise_poi_link['poi_id'] = enterprise_poi_link['poi_id'].astype(int)

# 添加主键e_id
enterprise_poi_link_output = pd.DataFrame({
    'e_id': range(1, len(enterprise_poi_link) + 1),
    'enterprise_id': enterprise_poi_link['enterprise_id'].values,
    'poi_id': enterprise_poi_link['poi_id'].values,
    'relationship_type': enterprise_poi_link['relationship_type'].values
})

enterprise_poi_link_output.to_csv('EnterprisePoiLink.csv', index=False, encoding='utf-8-sig')
print(f"✓ EnterprisePoiLink: {len(enterprise_poi_link_output)} 条记录")

# ==================== 6. LocationWeather（位置天气表） ====================
print("\n处理 LocationWeather 表...")
location_weather = df[['location_id', 'location_name', 'location_longitude', 'location_latitude', 
                       'current_temp', 'current_condition', 'weather_update_time']].copy()
location_weather = location_weather.drop_duplicates(subset=['location_id'])
location_weather = location_weather.sort_values('location_id')

location_weather_output = pd.DataFrame({
    'location_id': location_weather['location_id'].values,
    'location_name': location_weather['location_name'].values,
    'longitude': location_weather['location_longitude'].values,
    'latitude': location_weather['location_latitude'].values,
    'poi_id': np.nan,  # 可后续关联
    'temperature': location_weather['current_temp'].values,
    'conditions': location_weather['current_condition'].values,
    'update_time': location_weather['weather_update_time'].values
})

location_weather_output.to_csv('LocationWeather.csv', index=False, encoding='utf-8-sig')
print(f"✓ LocationWeather: {len(location_weather_output)} 条记录")

# ==================== 7. WeatherForecast（天气预报表） ====================
print("\n处理 WeatherForecast 表...")
locations = location_weather_output['location_id'].unique()
forecast_data = []
forecast_id = 1

base_date = datetime(2025, 12, 24)

for loc_id in locations:
    # 获取该location的当前温度作为基准
    loc_data = location_weather_output[location_weather_output['location_id'] == loc_id]
    if len(loc_data) > 0 and pd.notna(loc_data['temperature'].values[0]):
        base_temp = float(loc_data['temperature'].values[0])
    else:
        base_temp = 20.0
    
    # 生成未来7天的预报
    for day in range(1, 8):
        forecast_date = base_date + timedelta(days=day)
        # 模拟温度波动
        temp_variation = np.random.uniform(-3, 3)
        temp_max = round(base_temp + temp_variation + np.random.uniform(3, 6), 1)
        temp_min = round(base_temp + temp_variation - np.random.uniform(2, 4), 1)
        
        conditions = np.random.choice(['晴', '多云', '阴', '小雨', '雷阵雨'])
        
        forecast_data.append({
            'forecast_id': forecast_id,
            'location_id': int(loc_id),
            'forecast_date': forecast_date.strftime('%Y-%m-%d'),
            'temp_max': temp_max,
            'temp_min': temp_min,
            'condition_day': conditions
        })
        forecast_id += 1

weather_forecast = pd.DataFrame(forecast_data)
weather_forecast.to_csv('WeatherForecast.csv', index=False, encoding='utf-8-sig')
print(f"✓ WeatherForecast: {len(weather_forecast)} 条记录")

# ==================== 8. DynamicData（动态数据表） ====================
print("\n处理 DynamicData 表...")
# 为景点生成实时客流数据
scenic_pois = scenic_details_output['scenic_spot_id'].values
dynamic_data_list = []
record_id = 1

base_datetime = datetime(2025, 12, 24, 8, 0, 0)

# 取前50个景点或全部（如果少于50个）
selected_pois = scenic_pois[:min(50, len(scenic_pois))]

for poi_id in selected_pois:
    # 获取该景点的最大容量
    scenic_info = scenic_details_output[scenic_details_output['scenic_spot_id'] == poi_id]
    if len(scenic_info) > 0 and pd.notna(scenic_info['max_capacity'].values[0]):
        max_cap = float(scenic_info['max_capacity'].values[0])
    else:
        max_cap = 5000.0
    
    # 生成8:00-19:00的小时数据
    for hour in range(0, 12):
        record_time = base_datetime + timedelta(hours=hour)
        # 模拟客流量（早晚少，中午多）
        time_factor = 1.0 - abs(hour - 6) / 6 * 0.5
        passenger_flow = int(max_cap * np.random.uniform(0.2, 0.8) * time_factor)
        occupancy_rate = round(passenger_flow / max_cap, 2)
        
        dynamic_data_list.append({
            'record_id': record_id,
            'poi_id': int(poi_id),
            'record_time': record_time.strftime('%Y-%m-%d %H:%M:%S'),
            'passenger_flow': passenger_flow,
            'occupancy_rate': occupancy_rate
        })
        record_id += 1

dynamic_data_output = pd.DataFrame(dynamic_data_list)
dynamic_data_output.to_csv('DynamicData.csv', index=False, encoding='utf-8-sig')
print(f"✓ DynamicData: {len(dynamic_data_output)} 条记录")

# ==================== 9. WeatherAlert（天气预警表） ====================
print("\n处理 WeatherAlert 表...")
alert_data = []
alert_id = 1
base_time = datetime(2025, 12, 24, 8, 0, 0)

# 生成一些预警信息
alert_types = [
    ('暴雨黄色预警', '黄色', '生效中'),
    ('大风蓝色预警', '蓝色', '生效中'),
    ('雷电黄色预警', '黄色', '已解除'),
    ('高温橙色预警', '橙色', '生效中'),
    ('寒潮蓝色预警', '蓝色', '预警中')
]

for i, (title, level, status) in enumerate(alert_types, 1):
    alert_data.append({
        'alert_id': alert_id,
        'title': title,
        'level': level,
        'status': status,
        'publish_time': (base_time + timedelta(hours=i-1)).strftime('%Y-%m-%d %H:%M:%S')
    })
    alert_id += 1

weather_alert = pd.DataFrame(alert_data)
weather_alert.to_csv('WeatherAlert.csv', index=False, encoding='utf-8-sig')
print(f"✓ WeatherAlert: {len(weather_alert)} 条记录")

# ==================== 10. AlertAffectedPoi（预警影响POI表） ====================
print("\n处理 AlertAffectedPoi 表...")
affected_poi_data = []
a_id = 1

# 为每个预警随机分配受影响的POI
all_poi_ids = poi_master['poi_id'].values

for alert_id_val in weather_alert['alert_id']:
    # 每个预警影响5-15个POI
    num_affected = np.random.randint(5, 16)
    affected_pois = np.random.choice(all_poi_ids, 
                                    size=min(num_affected, len(all_poi_ids)), 
                                    replace=False)
    
    for poi_id in affected_pois:
        affected_poi_data.append({
            'a_id': a_id,
            'alert_id': int(alert_id_val),
            'poi_id': int(poi_id)
        })
        a_id += 1

alert_affected_poi = pd.DataFrame(affected_poi_data)
# 去重
alert_affected_poi = alert_affected_poi.drop_duplicates(subset=['alert_id', 'poi_id'])
# 重新分配a_id
alert_affected_poi['a_id'] = range(1, len(alert_affected_poi) + 1)

alert_affected_poi.to_csv('AlertAffectedPoi.csv', index=False, encoding='utf-8-sig')
print(f"✓ AlertAffectedPoi: {len(alert_affected_poi)} 条记录")

# ==================== 生成总结报告 ====================
print("\n" + "="*60)
print("数据拆分完成！生成文件列表：")
print("="*60)
print(f"1.  PoiMaster.csv                - {len(poi_master):6} 条")
print(f"2.  ScenicSpotDetails.csv        - {len(scenic_details_output):6} 条")
print(f"3.  HotelDetails.csv             - {len(hotel_details_output):6} 条")
print(f"4.  EnterpriseInfo.csv           - {len(enterprise_info_output):6} 条")
print(f"5.  EnterprisePoiLink.csv        - {len(enterprise_poi_link_output):6} 条")
print(f"6.  LocationWeather.csv          - {len(location_weather_output):6} 条")
print(f"7.  WeatherForecast.csv          - {len(weather_forecast):6} 条")
print(f"8.  DynamicData.csv              - {len(dynamic_data_output):6} 条")
print(f"9.  WeatherAlert.csv             - {len(weather_alert):6} 条")
print(f"10. AlertAffectedPoi.csv         - {len(alert_affected_poi):6} 条")
print("="*60)

# ==================== 数据验证 ====================
print("\n数据验证：")
print("="*60)

print("\nPOI类型分布：")
print(poi_master['poi_type'].value_counts())

print("\n景区等级分布：")
if len(scenic_details_output) > 0:
    print(scenic_details_output['level'].value_counts())

print("\n酒店星级分布：")
if len(hotel_details_output) > 0:
    print(hotel_details_output['star_rating'].value_counts())

print("\n企业类型分布：")
print(enterprise_info_output['enterprise_type'].value_counts())

print("\n外键关系检查：")

# 验证外键完整性
scenic_invalid = set(scenic_details_output['scenic_spot_id']) - set(poi_master['poi_id'])
print(f"✓ ScenicSpotDetails.scenic_spot_id: {len(scenic_invalid)} 个无效外键")

hotel_invalid = set(hotel_details_output['hotel_id']) - set(poi_master['poi_id'])
print(f"✓ HotelDetails.hotel_id: {len(hotel_invalid)} 个无效外键")

epl_enterprise_invalid = set(enterprise_poi_link_output['enterprise_id']) - set(enterprise_info_output['enterprise_id'])
epl_poi_invalid = set(enterprise_poi_link_output['poi_id']) - set(poi_master['poi_id'])
print(f"✓ EnterprisePoiLink.enterprise_id: {len(epl_enterprise_invalid)} 个无效外键")
print(f"✓ EnterprisePoiLink.poi_id: {len(epl_poi_invalid)} 个无效外键")

forecast_invalid = set(weather_forecast['location_id']) - set(location_weather_output['location_id'])
print(f"✓ WeatherForecast.location_id: {len(forecast_invalid)} 个无效外键")

if len(dynamic_data_output) > 0:
    dynamic_invalid = set(dynamic_data_output['poi_id']) - set(poi_master['poi_id'])
    print(f"✓ DynamicData.poi_id: {len(dynamic_invalid)} 个无效外键")

aap_alert_invalid = set(alert_affected_poi['alert_id']) - set(weather_alert['alert_id'])
aap_poi_invalid = set(alert_affected_poi['poi_id']) - set(poi_master['poi_id'])
print(f"✓ AlertAffectedPoi.alert_id: {len(aap_alert_invalid)} 个无效外键")
print(f"✓ AlertAffectedPoi.poi_id: {len(aap_poi_invalid)} 个无效外键")

print("\n" + "="*60)
print("所有CSV文件已生成，可以导入MySQL数据库！")
print("="*60)