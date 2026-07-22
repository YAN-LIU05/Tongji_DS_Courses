import requests
from bs4 import BeautifulSoup
import re
import json

# --- 任务一：分析动态加载数据的来源 ---
def find_data_source(soup_obj):
    """
    分析HTML，找出 'hour3data' 变量的来源。
    """
    print("\n" + "="*20 + " 任务一：分析动态加载数据的来源 " + "="*20)
    
    # 查找所有不含 'src' 属性的 <script> 标签（即内联脚本）
    all_scripts = soup_obj.find_all('script', src=None)
    all_scripts_text = "\n".join([s.get_text() for s in all_scripts])
    print(f"页面中共找到 {len(all_scripts)} 个内联 <script> 标签。")
    found_in_script = False
    for script in all_scripts:
        # 检查<script>标签内是否有文本内容，并且是否包含目标变量
        if script.string and 'hour3data' in script.string:
            print("✅ 找到包含 hour3data 的 <script> 段落。")

            # ✅ 提取 hour3data 内的第一个 {...}
            match = re.search(r"var\s+hour3data\s*=\s*(\{.*?\});", all_scripts_text, re.DOTALL)

            if match:
                json_string = match.group(1)

                # ✅ 手动括号配对，确保只取第一个完整 JSON 对象
                brace_count = 0
                end_index = 0
                for i, ch in enumerate(json_string):
                    if ch == '{':
                        brace_count += 1
                    elif ch == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            end_index = i + 1
                            break
                json_string = json_string[:end_index]

                # ✅ 尝试修复乱码（编码错误）
                try:
                    json_string_fixed = json_string.encode('latin1').decode('utf-8')
                except UnicodeEncodeError:
                    json_string_fixed = json_string  # 如果不需要修复则保留原文

                print(json_string_fixed)

                print("\n✅ 成功提取到 hour3data 的第一个 JSON 对象。")
                print(json_string_fixed[:200] + " ... [内容省略]")

                print("✅ 接下来，对该字符串进行验证分析...")

                try:
                    data = json.loads(json_string_fixed)
                    print("✅ 成功将字符串解析为 Python 字典进行验证。")

                    if '1d' in data:
                        print(f"    - 验证成功：找到了 '1d' 键，包含 {len(data['1d'])} 条数据。")
                    else:
                        print("    - 注意：未找到 '1d' 键，但 JSON 结构有效。")

                except json.JSONDecodeError as e:
                    print("❌ JSON 解析失败：", e)

            else:
                print("❌ 未能通过正则表达式提取出完整的 hour3data 对象。")

            found_in_script = True
            break  # 找到后退出循环
            
    if not found_in_script:
        print("❌ 未在任何内嵌 <script> 标签中找到 'hour3data' 变量。")
        
def find_dynamic_insertion_elements(soup_obj):
    """
    查找JS动态插入内容的“数据源”和“目标容器”。
    """
    print("\n" + "="*20 + " 任务二：查找 JS 动态插入的元素 " + "="*20)
    
    # 1. 验证数据源的存在
    data_script_exists = bool(soup_obj.find(string=re.compile("var hour3data")))
    if data_script_exists:
        print("✅ 找到了包含 'hour3data' 数据的 <script> 标签 (数据源已就绪)。")
    else:
        print("❌ 未找到 'hour3data' 数据源。")
        
    # 2. 验证目标容器的存在
    target_container = soup_obj.find(id="curve")
    if target_container:
        print(f"✅ 找到了准备接收动态内容的目标容器: <{target_container.name} id=\"{target_container.get('id')}\" class=\"{target_container.get('class')[0]}\">")
        
        # 3. 检查容器当前是否为空
        if not target_container.find_all(recursive=False):
            print("    - 容器在原始HTML中是空的，这完全符合“等待JS动态插入内容”的特征。")
        else:
            print("    - 注意：容器内部已有内容，可能是静态的框架。")
    else:
        print("❌ 未找到 ID 为 'curve' 的目标容器。")
        
    if data_script_exists and target_container:
        print("\n[结论]: 页面同时提供了【数据源('hour3data'变量)】和【目标容器(id='curve')】。JS脚本负责读取数据源，生成HTML，并填充到目标容器中。")

# --- 任务三：识别定时刷新的数据区域 ---
def find_periodic_refresh_clues(soup_obj):
    """
    从HTML中寻找与定时刷新相关的线索。
    """
    print("\n" + "="*20 + " 任务三：识别定时刷新的数据区域 " + "="*20)
    
    # 1. 寻找实时数据相关的变量线索
    # `observe24h_data` 存储了过去24小时的实况数据，是定时刷新的目标
    realtime_data_script = soup_obj.find(string=re.compile("var observe24h_data"))
    if realtime_data_script:
        print("✅ 找到了包含过去24小时实况数据的变量 'observe24h_data'。这是页面顶部“实况天气”模块的数据源。")
    else:
        # 有时实况数据是通过一个叫 dataSK 的变量加载的
        realtime_data_script_sk = soup_obj.find(string=re.compile("var dataSK"))
        if realtime_data_script_sk:
            print("✅ 找到了包含实况数据的变量 'dataSK'。这是页面顶部“实况天气”模块的数据源。")
        else:
            print("❌ 未在内联脚本中找到明显的实况数据变量（如 'observe24h_data' 或 'dataSK'）。")

    # 2. 寻找发起异步请求的代码线索
    xhr_script = soup_obj.find(string=re.compile("XMLHttpRequest"))
    if xhr_script:
        print("✅ 找到了使用 'XMLHttpRequest' (发起XHR/AJAX请求) 的内联代码。")
    else:
        print("❌ 在内联脚本中未直接找到使用 'XMLHttpRequest' 的代码（可能封装在外部JS文件中）。")
        


# --- 主程序入口 ---
if __name__ == "__main__":
    target_url = "http://www.weather.com.cn/weather/101020100.shtml"
    
    print(f"正在从 URL 获取 HTML 内容: {target_url}\n")
    
    try:
        # 发送网络请求，并伪装成浏览器
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(target_url, headers=headers, timeout=10)
        # 如果请求失败（如404），则抛出异常
        response.raise_for_status()

        # 使用 BeautifulSoup 解析获取到的 HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 依次执行三个分析任务
        find_data_source(soup)
        find_dynamic_insertion_elements(soup)
        find_periodic_refresh_clues(soup)

    except requests.exceptions.RequestException as e:
        print(f"网络请求失败: {e}")
    except Exception as e:
        print(f"发生未知错误: {e}")