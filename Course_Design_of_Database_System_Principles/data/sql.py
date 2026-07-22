import pandas as pd
import numpy as np

# 读取所有CSV文件
csv_files = {
    'PoiMaster': 'PoiMaster.csv',
    'ScenicSpotDetails': 'ScenicSpotDetails.csv',
    'HotelDetails': 'HotelDetails.csv',
    'EnterpriseInfo': 'EnterpriseInfo.csv',
    'EnterprisePoiLink': 'EnterprisePoiLink.csv',
    'LocationWeather': 'LocationWeather.csv',
    'WeatherForecast': 'WeatherForecast.csv',
    'DynamicData': 'DynamicData.csv',
    'WeatherAlert': 'WeatherAlert.csv',
    'AlertAffectedPoi': 'AlertAffectedPoi.csv'
}

def escape_sql_string(value):
    """转义SQL字符串"""
    if pd.isna(value):
        return 'NULL'
    if isinstance(value, str):
        # 转义单引号和反斜杠
        value = value.replace('\\', '\\\\').replace("'", "\\'")
        return f"'{value}'"
    return str(value)

def generate_insert_sql(table_name, df):
    """生成INSERT语句"""
    sql_statements = []
    
    # 分批插入，每500条一批
    batch_size = 500
    
    for start in range(0, len(df), batch_size):
        end = min(start + batch_size, len(df))
        batch = df.iloc[start:end]
        
        columns = ', '.join([f'`{col}`' for col in df.columns])
        
        values_list = []
        for _, row in batch.iterrows():
            values = ', '.join([escape_sql_string(val) for val in row])
            values_list.append(f'({values})')
        
        values_str = ',\n  '.join(values_list)
        
        sql = f"INSERT INTO `{table_name}` ({columns})\nVALUES\n  {values_str};\n"
        sql_statements.append(sql)
    
    return sql_statements

# 生成SQL文件
print("正在生成SQL导入文件...")

# 询问数据库名称
db_name = input("请输入数据库名称（默认: tourism_db）: ").strip()
if not db_name:
    db_name = 'tourism_db'

with open('import_data.sql', 'w', encoding='utf-8') as f:
    f.write("-- 数据导入SQL脚本\n")
    f.write("-- 生成时间: " + pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S') + "\n\n")
    
    # 添加这些重要的设置
    f.write(f"-- 选择数据库\n")
    f.write(f"USE `{db_name}`;\n\n")
    f.write("-- 设置字符集和外键检查\n")
    f.write("SET NAMES utf8mb4;\n")
    f.write("SET CHARACTER_SET_CLIENT = utf8mb4;\n")
    f.write("SET CHARACTER_SET_CONNECTION = utf8mb4;\n")
    f.write("SET FOREIGN_KEY_CHECKS = 0;\n\n")
    
    # 按顺序导入
    import_order = [
        'PoiMaster',
        'EnterpriseInfo',
        'WeatherAlert',
        'ScenicSpotDetails',
        'HotelDetails',
        'EnterprisePoiLink',
        'LocationWeather',
        'WeatherForecast',
        'DynamicData',
        'AlertAffectedPoi'
    ]
    
    for table_name in import_order:
        print(f"处理 {table_name}...")
        
        df = pd.read_csv(csv_files[table_name])
        
        f.write(f"-- ==================== {table_name} ====================\n")
        f.write(f"-- 共 {len(df)} 条记录\n\n")
        
        sql_statements = generate_insert_sql(table_name, df)
        
        for sql in sql_statements:
            f.write(sql)
            f.write("\n")
        
        print(f"✓ {table_name}: {len(df)} 条记录")
    
    f.write("-- 恢复外键检查\n")
    f.write("SET FOREIGN_KEY_CHECKS = 1;\n")
    f.write("\n-- 导入完成！\n")

print("\n" + "="*60)
print(f"SQL文件生成完成: import_data.sql")
print(f"目标数据库: {db_name}")
print("="*60)
print("\n使用方法：")
print("方法1 - MySQL Workbench:")
print("  1. 在左侧SCHEMAS列表中双击你的数据库名")
print("  2. File → Open SQL Script → 选择 import_data.sql")
print("  3. 点击执行按钮（⚡闪电图标）")
print("\n方法2 - 命令行:")
print(f"  mysql -u root -p {db_name} < import_data.sql")
print("="*60)