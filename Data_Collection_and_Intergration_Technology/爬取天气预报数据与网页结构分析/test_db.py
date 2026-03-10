import sqlite3
import pandas as pd # 使用pandas可以让输出更美观

def check_database_data(db_name, table_name):
    """连接到数据库并打印指定表的所有内容。"""
    try:
        # 使用 with 语句确保连接安全关闭
        with sqlite3.connect(db_name) as conn:
            print(f"--- 正在查询数据库 '{db_name}' 中的表 '{table_name}' ---")
            
            # 使用pandas的read_sql_query函数，可以直接将查询结果转为DataFrame
            # "SELECT * FROM ..." 表示查询表中的所有列和所有行
            query = f"SELECT * FROM {table_name};"
            df = pd.read_sql_query(query, conn)

            if df.empty:
                print("查询成功，但该表中没有任何数据。")
            else:
                print("查询成功！数据如下：")
                # 打印整个DataFrame
                print(df.to_string()) # 使用 .to_string() 保证所有行列都能显示全
        
    except sqlite3.OperationalError:
        print(f"错误：无法找到表 '{table_name}' 或数据库 '{db_name}' 不存在。")
    except Exception as e:
        print(f"发生了一个错误: {e}")

if __name__ == "__main__":
    # 验证第一个数据库
    check_database_data(
        db_name="weather_history.db", 
        table_name="shanghai_weather_202509"
    )
    
    print("\n" + "="*50 + "\n")

    # 验证第二个数据库
    check_database_data(
        db_name="weather_forecast.db",
        table_name="shanghai_hourly"
    )