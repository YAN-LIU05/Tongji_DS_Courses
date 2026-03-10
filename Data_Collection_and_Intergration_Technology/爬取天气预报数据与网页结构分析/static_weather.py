import requests
from bs4 import BeautifulSoup, Tag
import pandas as pd
import sqlite3  # 导入SQLite库

def get_element_signature(element):
    """
    为HTML元素生成一个简洁的签名，包含标签名、ID和类。
    """
    if not isinstance(element, Tag):
        return str(element)
        
    signature = f"<{element.name}"
    
    element_id = element.get('id')
    if element_id:
        signature += f' id="{element_id}"'
        
    element_class = element.get('class')
    if element_class:
        signature += f' class="{" ".join(element_class)}"'
        
    signature += ">"
    return signature

def generate_dynamic_dom_tree(target_element):
    """
    从目标元素开始，向上追溯并动态生成到<body>的DOM结构树。
    """
    print("\n" + "="*50 + "\n")
    print("根据本次爬取结果动态生成的DOM结构树:")

    if not target_element:
        print("错误：未能定位到目标元素，无法生成DOM树。")
        return

    path_to_body = []
    current_element = target_element
    for parent in current_element.parents:
        path_to_body.append(parent)
        if parent.name == 'body':
            break
            
    path_to_body.reverse()

    indentation = "    "
    for i, element in enumerate(path_to_body):
        print(f"{indentation * i}└── {get_element_signature(element)}")

    print(f"{indentation * len(path_to_body)}└── {get_element_signature(target_element)}  (← **数据父容器**)")
    
    first_li = target_element.find('li')
    if first_li:
        li_indent = indentation * (len(path_to_body) + 1)
        print(f"{li_indent}│")
        print(f"{li_indent}├── {get_element_signature(first_li)}  (← **单日数据容器**)")
        
        divs = first_li.find_all('div')
        div_indent = li_indent + "    "
        if len(divs) == 5:
            print(f"{div_indent}├── {get_element_signature(divs[0])} (a) 日期")
            print(f"{div_indent}├── {get_element_signature(divs[1])} (b) 最高温")
            print(f"{div_indent}├── {get_element_signature(divs[2])} (b) 最低温")
            print(f"{div_indent}├── {get_element_signature(divs[3])} (c) 天气状况")
            print(f"{div_indent}└── {get_element_signature(divs[4])} (d) 风力风向")
            
        print(f"{li_indent}│")
        print(f"{li_indent}└── ... (后续 <li> 结构与此相同)")
    print("\n")


def scrape_shanghai_weather(url):
    """
    从指定的tianqi.com网址爬取上海的历史天气数据。
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        weather_list_container = soup.find('ul', class_='thrui')
        
        if not weather_list_container:
            print("错误：未能找到天气数据的容器（<ul class='thrui'>）。网页结构可能已更改。")
            return None, None

        weather_data = []
        for day_item in weather_list_container.find_all('li'):
            details = day_item.find_all('div')
            if len(details) == 5:
                date = details[0].get_text(strip=True)
                # 清洗数据，去掉'℃'符号，便于存入数据库
                max_temp = details[1].get_text(strip=True).replace('℃', '')
                min_temp = details[2].get_text(strip=True).replace('℃', '')
                weather_condition = details[3].get_text(strip=True)
                wind = details[4].get_text(strip=True)

                weather_data.append({
                    "日期": date,
                    "最高温": max_temp + '℃',
                    "最低温": min_temp + '℃',
                    "天气状况": weather_condition,
                    "风力风向": wind
                })

        return weather_data, weather_list_container

    except requests.exceptions.RequestException as e:
        print(f"网络请求错误: {e}")
        return None, None
    except Exception as e:
        print(f"发生了一个未知错误: {e}")
        return None, None

# --- 新增函数：将数据存入SQLite ---
def save_to_sqlite(data, db_name="weather_history.db", table_name="shanghai_202509"):
    """
    将天气数据列表存入SQLite数据库。

    Args:
        data (list): 包含天气数据字典的列表。
        db_name (str): 数据库文件名。
        table_name (str): 数据表名。
    """
    if not data:
        print("没有数据可存入SQLite。")
        return
    
    # 使用 with 语句可以确保数据库连接在使用后自动关闭
    try:
        with sqlite3.connect(db_name) as conn:
            cursor = conn.cursor()

            # 1. 创建表（如果表已存在，则不执行任何操作）
            #    - record_date 设置为 UNIQUE，防止同一天的数据被重复插入
            create_table_sql = f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                record_date DATE NOT NULL UNIQUE,
                max_temp INTEGER,
                min_temp INTEGER,
                weather TEXT,
                wind TEXT
            );
            """
            cursor.execute(create_table_sql)

            # 2. 准备要插入的数据
            #    将字典列表转换为元组列表，以匹配SQL的 '?' 占位符
            rows_to_insert = [
                (item['日期'], item['最高温'], item['最低温'], item['天气状况'], item['风力风向']) 
                for item in data
            ]
            
            # 3. 插入数据
            #    使用 INSERT OR IGNORE，如果日期已存在（违反UNIQUE约束），则忽略该条插入，不会报错
            insert_sql = f"""
            INSERT OR IGNORE INTO {table_name} (record_date, max_temp, min_temp, weather, wind) 
            VALUES (?, ?, ?, ?, ?);
            """
            
            # executemany 可以高效地执行多次插入
            cursor.executemany(insert_sql, rows_to_insert)

            # with 语句会自动调用 conn.commit()
            print(f"\n数据已成功存入SQLite数据库 '{db_name}' 的 '{table_name}' 表中。")
            # 打印本次操作实际插入的行数
            print(f"本次操作新增了 {cursor.rowcount} 条记录。")

    except sqlite3.Error as e:
        print(f"SQLite操作失败: {e}")

# --- 主程序入口 ---
if __name__ == "__main__":
    target_url = "https://lishi.tianqi.com/shanghai/202509.html"
    
    print(f"正在从 {target_url} 爬取数据...")
    
    scraped_data, target_element = scrape_shanghai_weather(target_url)

    if scraped_data and target_element:
        print("\n数据爬取成功！\n")
        
        # 使用pandas展示数据
        df = pd.DataFrame(scraped_data)
        print("爬取到的数据预览:")
        print(df)
        
        # 动态生成DOM树
        generate_dynamic_dom_tree(target_element)
        
        # --- 将数据存入SQLite数据库 ---
        save_to_sqlite(scraped_data, table_name="shanghai_weather_202509")
        
    else:
        print("\n数据爬取失败。请检查URL或网络连接。")