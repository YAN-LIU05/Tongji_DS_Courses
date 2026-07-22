import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

def plot_temperature_curve(db_name="weather_history.db", table_name="shanghai_weather_202509"):
    """
    从SQLite数据库中读取指定表格的天气数据，并绘制温度变化曲线图。
    """
    try:
        print(f"正在连接到数据库: {db_name}")
        with sqlite3.connect(db_name) as conn:
            query = f"SELECT record_date, max_temp, min_temp FROM {table_name} ORDER BY record_date;"
            print(f"正在执行查询: {query}")
            df = pd.read_sql_query(query, conn)

    except sqlite3.OperationalError as e:
        print(f"数据库操作错误: {e}")
        print(f"请确保数据库文件 '{db_name}' 和数据表 '{table_name}' 已存在且名称正确。")
        return
    except Exception as e:
        print(f"发生未知错误: {e}")
        return

    if df.empty:
        print("错误：未能从数据库中获取到任何数据，无法绘图。")
        return
        
    print("\n成功获取原始数据，预览如下:")
    print(df.head())
    print("\n原始数据类型:")
    df.info()

    # --- 【核心修正部分】：数据清洗和类型转换 ---
    print("\n--- 正在进行数据清洗和类型转换 ---")
    
    # 1. 【新增步骤】：从 'record_date' 文本中提取出日期部分
    #    例如，从 "2025-09-01 星期一" 中提取 "2025-09-01"
    print("正在清理 'record_date' 列，移除多余的文本...")
    df['record_date'] = df['record_date'].str.split(' ').str[0]
    print("\n清理后的 'record_date' 列预览:")
    print(df.head())

    # 2. 现在，可以安全地转换日期列了
    df['record_date'] = pd.to_datetime(df['record_date'], format='%Y-%m-%d', errors='coerce')

    # 3. 转换温度列（作为安全检查，即使现在类型正确）
    df['max_temp'] = pd.to_numeric(df['max_temp'], errors='coerce')
    df['min_temp'] = pd.to_numeric(df['min_temp'], errors='coerce')

    # 4. 删除可能在转换过程中产生的任何坏数据行
    df.dropna(inplace=True)

    if df.empty:
        print("错误：数据清洗后没有剩余的有效数据，无法绘图。请检查数据库内容。")
        return
        
    print("\n数据清洗和转换完成，处理后数据类型如下:")
    df.info()

    # --- 3. 开始绘图 ---
    print("\n正在生成温度曲线图...")
    try:
        plt.rcParams['font.sans-serif'] = ['SimHei']
        plt.rcParams['axes.unicode_minus'] = False
    except:
        print("警告：未能设置中文字体'SimHei'。")

    plt.figure(figsize=(16, 8))
    
    days = df['record_date'].dt.strftime('%d')

    plt.plot(days, df['max_temp'], marker='o', linestyle='-', color='red', label='最高温度')
    plt.plot(days, df['min_temp'], marker='s', linestyle='--', color='blue', label='最低温度')
    
    # --- 4. 美化图表 ---
    plt.fill_between(days, df['max_temp'], df['min_temp'], color='gray', alpha=0.15)
    
    # 将温度值转换为整数再显示，避免出现 .0
    for a, b in zip(days, df['max_temp']):
        plt.text(a, b + 0.3, f'{int(b)}°', ha='center', va='bottom', fontsize=9)
    for a, b in zip(days, df['min_temp']):
        plt.text(a, b - 0.2, f'{int(b)}°', ha='center', va='top', fontsize=9)

    plt.title('2025年9月上海市每日温度变化曲线图', fontsize=20)
    plt.xlabel('日期（9月）', fontsize=12)
    plt.ylabel('温度 (°C)', fontsize=12)
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()

    # 5. 显示图表
    print("图表已生成，即将显示...")
    plt.show()


# --- 主程序入口 ---
if __name__ == "__main__":
    plot_temperature_curve(
        db_name="weather_history.db", 
        table_name="shanghai_weather_202509"
    )