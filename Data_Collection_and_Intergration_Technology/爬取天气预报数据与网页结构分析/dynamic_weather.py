import time
import json
import sqlite3
from datetime import datetime, date, timedelta

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# --- 函数：为 Selenium 元素生成签名 (无变动) ---
def get_element_signature_selenium(element):
    """为 Selenium 的 WebElement 生成一个简洁的签名。"""
    signature = f"<{element.tag_name}"
    element_id = element.get_attribute('id')
    if element_id:
        signature += f' id="{element_id}"'
    element_class = element.get_attribute('class')
    if element_class:
        signature += f' class="{element_class}"'
    signature += ">"
    return signature

# --- 函数：使用 Selenium 生成 DOM 树 (无变动) ---
def generate_dynamic_dom_tree_selenium(target_element):
    """
    从目标 Selenium 元素开始，向上追溯并动态生成到<body>的DOM结构树。
    这个版本会打印出每个节点的简洁签名（标签名、ID、类名）。
    """
    if not target_element:
        print("错误：传入的目标元素无效。")
        return

    print("\n" + "="*20 + " 动态内容DOM结构追溯 " + "="*20)
    print(f"起始元素: {get_element_signature_selenium(target_element)}")
    print("-" * (42 + len(" 动态内容DOM结构追溯 ")))

    path_to_body = []
    current_element = target_element

    # 循环向上追溯父元素，直到 body 或 html 标签
    while current_element.tag_name not in ['body', 'html']:
        path_to_body.append(current_element)
        try:
            # 使用 XPath '..' 来获取父元素
            parent_element = current_element.find_element(By.XPATH, '..')
            current_element = parent_element
        except NoSuchElementException:
            # 如果找不到父元素（极少见，除非DOM结构异常），则停止
            print("警告：在追溯过程中某个元素没有父节点，已到达DOM树顶端。")
            break
    
    # 将 body 标签也加入路径中
    if current_element.tag_name == 'body':
        path_to_body.append(current_element)

    # 反转列表，从 body 开始打印
    path_to_body.reverse()

    # 打印DOM树结构
    indent_level = 0
    for element in path_to_body:
        indent = "  " * indent_level
        signature = get_element_signature_selenium(element)
        
        # 判断当前元素是否为我们最开始的目标元素
        if element == target_element:
            print(f"{indent}{signature}  <-- [目标容器]")
        else:
            print(f"{indent}{signature}")
        
        indent_level += 1
    
    print("\n" + "="*50 + "\n")


# --- 【已修正的函数】：将逐小时天气数据存入SQLite ---
def save_hourly_forecast_to_sqlite(data, db_name="weather_forecast.db", table_name="shanghai_hourly"):
    """
    将逐小时天气预报数据存入SQLite数据库。
    """
    if not data:
        print("没有数据可存入SQLite。")
        return
    
    try:
        with sqlite3.connect(db_name) as conn:
            cursor = conn.cursor()

            create_table_sql = f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                forecast_datetime TEXT NOT NULL UNIQUE,
                weather_condition TEXT,
                temperature_celsius INTEGER,
                wind_direction TEXT,
                wind_force TEXT
            );
            """
            cursor.execute(create_table_sql)

            rows_to_insert = []
            today = date.today()

            for item in data:
                time_str = item['time']  # e.g., "08日23时"

                # --- 【核心修正部分】 ---
                # 1. 更稳健地解析时间和日期
                try:
                    # 替换掉所有非数字字符，然后根据长度判断
                    cleaned_str = ''.join(filter(str.isdigit, time_str))
                    
                    if len(cleaned_str) > 2: # 格式是 "DDHH", e.g., "0823"
                        forecast_day = int(cleaned_str[:-2])
                        forecast_hour = int(cleaned_str[-2:])
                    else: # 格式是 "HH", e.g., "23"
                        forecast_day = today.day
                        forecast_hour = int(cleaned_str)

                except (ValueError, IndexError):
                    print(f"警告：无法解析时间字符串 '{time_str}'，跳过此条记录。")
                    continue # 跳过这一条错误数据

                # 2. 更精确地处理跨月/跨年
                current_year = today.year
                current_month = today.month

                # 如果预报的日期小于今天的日期（例如，在30号爬取到了1号的数据），说明月份+1
                if forecast_day < today.day:
                    if current_month == 12:
                        current_month = 1
                        current_year += 1
                    else:
                        current_month += 1
                
                # 3. 构建完整的日期时间对象，避免无效日期
                try:
                    full_datetime_obj = datetime(current_year, current_month, forecast_day, forecast_hour)
                    full_datetime_str = full_datetime_obj.strftime('%Y-%m-%d %H:%M:%S')
                except ValueError:
                    print(f"警告：无法构建有效日期 {current_year}-{current_month}-{forecast_day}，跳过。")
                    continue
                
                temperature = int(item['temperature'].replace('℃', ''))

                rows_to_insert.append((
                    full_datetime_str,
                    item['weather_condition'],
                    temperature,
                    item['wind_direction'],
                    item['wind_force']
                ))

            insert_sql = f"""
            INSERT OR IGNORE INTO {table_name} 
            (forecast_datetime, weather_condition, temperature_celsius, wind_direction, wind_force)
            VALUES (?, ?, ?, ?, ?);
            """
            cursor.executemany(insert_sql, rows_to_insert)

            print(f"\n数据已成功存入SQLite数据库 '{db_name}' 的 '{table_name}' 表中。")
            print(f"本次操作新增了 {cursor.rowcount} 条记录。")

    except sqlite3.Error as e:
        print(f"SQLite操作失败: {e}")


# --- 主程序 (无变动) ---
if __name__ == "__main__":
    CHROMEDRIVER_PATH = r"D:\chromedriver-win64\chromedriver.exe" 
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")

    service = Service(executable_path=CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=chrome_options)

    url = "http://www.weather.com.cn/weather/101020100.shtml"

    try:
        print(f"正在访问目标网页: {url}")
        driver.get(url)
        time.sleep(2)

        print("正在提取逐小时天气数据...")
        hourly_data_js = driver.execute_script("return hour3data;")
        
        data_extraction_successful = False
        if not hourly_data_js:
            print("未能成功提取到 hour3data 变量。")
        else:
            hourly_forecast_list = hourly_data_js.get('1d')
            if not hourly_forecast_list:
                 print("未能找到'1d'键对应的逐小时预报数据。")
            else:
                collected_data = []
                for forecast_str in hourly_forecast_list:
                    parts = forecast_str.split(',')
                    collected_data.append({
                        "time": parts[0],
                        "weather_condition": parts[2],
                        "temperature": parts[3],
                        "wind_direction": parts[4],
                        "wind_force": parts[5]
                    })

                print("\n--- 上海市未来24小时逐小时天气预报 ---\n")
                print(f"{'时间':<12} | {'天气状况':<10} | {'温度':<8} | {'风向':<10} | {'风力':<10}")
                print("-" * 60)
                for item in collected_data:
                    print(f"{item['time']:<12} | {item['weather_condition']:<10} | {item['temperature']:<8} | {item['wind_direction']:<10} | {item['wind_force']:<10}")
                
                print("\n数据爬取成功！")
                data_extraction_successful = True

                save_hourly_forecast_to_sqlite(collected_data)

        if data_extraction_successful:
            try:
                wait = WebDriverWait(driver, 5)
                locator = (By.ID, "curve")
                print(f"\n正在使用最终正确的定位器定位容器: id='curve'...")
                target_container_element = wait.until(EC.visibility_of_element_located(locator))
                print("成功定位到目标容器！")
                generate_dynamic_dom_tree_selenium(target_container_element) # 可以取消注释来显示DOM树
            except TimeoutException:
                print("\n错误：虽然数据已提取，但在指定时间内未能定位到动态内容容器(id='curve')。")

    except Exception as e:
        print(f"爬取过程中发生错误: {e}")

    finally:
        print("关闭浏览器...")
        driver.quit()