import pymysql
import requests
from bs4 import BeautifulSoup
import time
import random
import urllib3
import ssl
import re

# =========================
# 配置
# =========================
# 禁用 SSL 警告
ssl._create_default_https_context = ssl._create_unverified_context
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'lzz20050511',  # 记得提交作业时打码
    'database': 'gitTrend_db',
    'charset': 'utf8mb4'
}

# 伪装头
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
}

def db_connect():
    return pymysql.connect(**DB_CONFIG)

def clean_readme(text):
    """简单清洗文本"""
    if not text:
        return None
    # 去除多余的空行
    return re.sub(r'\n\s*\n', '\n', text.strip())

def fetch_readme_from_github(url):
    """
    访问 GitHub 详情页并提取 README 内容
    """
    try:
        # 随机延时，模拟人类行为，非常重要！
        sleep_time = random.uniform(1.5, 3.5)
        print(f"   waiting {sleep_time:.2f}s...", end="")
        time.sleep(sleep_time)

        resp = requests.get(url, headers=HEADERS, verify=False, timeout=15)
        
        if resp.status_code != 200:
            print(f" [Error: {resp.status_code}]", end="")
            return None

        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # 寻找 README 的容器
        # GitHub 通常用 'markdown-body' 类来包裹 README
        readme_div = soup.find('article', {'class': 'markdown-body'})
        
        if readme_div:
            return clean_readme(readme_div.get_text())
        else:
            print(" [No README Found]", end="")
            return None

    except Exception as e:
        print(f" [Exception: {e}]", end="")
        return None

def main():
    conn = db_connect()
    if not conn:
        print("数据库连接失败")
        return

    try:
        with conn.cursor() as cursor:
            # 1. 查找所有 readme 为空，或者 readme 是空字符串的记录
            # 这里假设你的表里有 'repo' 或 'url' 字段，最好用 id 或 repo 唯一定位
            # 注意：如果你的表没有 id 主键，请使用 repo 作为条件
            print("正在查询待处理的任务...")
            sql_select = """
                SELECT repo, url 
                FROM github_trending_day 
                WHERE readme IS NULL OR readme = ''
            """
            cursor.execute(sql_select)
            tasks = cursor.fetchall()
            
            total = len(tasks)
            print(f"共发现 {total} 个项目需要抓取 README。\n")

            for index, (repo, url) in enumerate(tasks):
                print(f"[{index+1}/{total}] 处理: {repo} ...", end="")
                
                # 2. 爬取内容
                content = fetch_readme_from_github(url)

                if content:
                    # 3. 更新数据库
                    # 注意：这里根据 repo 更新，如果同一天有重复 repo 可能会都更新，问题不大
                    # 更好的做法是 SELECT 时带上 id，UPDATE 时根据 id 更新
                    sql_update = """
                        UPDATE github_trending_day 
                        SET readme = %s 
                        WHERE repo = %s
                    """
                    cursor.execute(sql_update, (content, repo))
                    conn.commit()
                    print(" -> [Saved]")
                else:
                    # 如果抓取失败，可以选择标记一下，或者下次继续抓
                    print(" -> [Skipped]")

    except Exception as e:
        print(f"\n发生错误: {e}")
    finally:
        conn.close()
        print("\n所有任务结束。")

if __name__ == '__main__':
    main()