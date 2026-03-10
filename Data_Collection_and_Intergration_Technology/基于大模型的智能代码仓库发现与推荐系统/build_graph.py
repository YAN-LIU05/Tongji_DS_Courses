import pymysql
import requests
import time
import random
import urllib3
import ssl
from urllib.parse import urlparse

# =========================
# 配置
# =========================
ssl._create_default_https_context = ssl._create_unverified_context
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 【可选】如果你有 GitHub Token，填在这里，速度更快且不限流
# 申请地址: https://github.com/settings/tokens (选 Classic, 勾选 public_repo)
GITHUB_TOKEN = ""  # 例如 "ghp_xxxxxxxxxxxx"

DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'lzz20050511', # 密码
    'database': 'gitTrend_db',
    'charset': 'utf8mb4'
}

# 数据库中 URL 的 Collation 冲突问题解决：
# 确保在 SQL 比较时使用 COLLATE utf8mb4_unicode_ci

def db_connect():
    return pymysql.connect(**DB_CONFIG)

def get_repo_path(url):
    """
    从 https://github.com/owner/repo 提取 owner/repo
    """
    parsed = urlparse(url)
    path = parsed.path.strip('/')
    return path

def get_contributors_from_api(repo_url):
    """
    使用 GitHub API 获取贡献者
    """
    repo_path = get_repo_path(repo_url) # 变成 "torvalds/linux"
    api_url = f"https://api.github.com/repos/{repo_path}/contributors?per_page=10" # 只取前10个大神
    
    headers = {
        'Accept': 'application/vnd.github.v3+json',
        'User-Agent': 'Mozilla/5.0 (Student Project)',
    }
    
    # 如果有 Token，加上去
    if GITHUB_TOKEN:
        headers['Authorization'] = f'token {GITHUB_TOKEN}'
    
    contributors = []
    
    try:
        print(f"   API请求: {api_url} ...", end="")
        resp = requests.get(api_url, headers=headers, verify=False, timeout=10)
        
        if resp.status_code == 200:
            data = resp.json()
            for item in data:
                # API 返回的数据非常标准
                contributors.append({
                    'name': item['login'], # 用户名
                    'url': item['html_url'], # 主页
                    'avatar': item['avatar_url'] # 头像
                })
            print(" [OK]")
        elif resp.status_code == 403:
            print(" [Rate Limit Exceeded] API限流了，请休息一小时或使用 Token")
        elif resp.status_code == 404:
            print(" [404] 仓库不存在或改名了")
        else:
            print(f" [Error {resp.status_code}]")
            
    except Exception as e:
        print(f" [Exception: {e}]")
        
    return contributors

def main():
    conn = db_connect()
    if not conn:
        print("数据库连接失败")
        return

    try:
        with conn.cursor() as cursor:
            # 1. 修复 Collation 冲突的查询语句
            print("正在获取任务列表...")
            # 强制指定字符集比较，防止报错
            sql_tasks = """
                SELECT DISTINCT url 
                FROM github_trending_day 
                WHERE url COLLATE utf8mb4_unicode_ci NOT IN (
                    SELECT DISTINCT repo_url COLLATE utf8mb4_unicode_ci FROM repo_contributors
                )
            """
            cursor.execute(sql_tasks)
            repos = cursor.fetchall()
            
            total = len(repos)
            print(f"共有 {total} 个项目需要构建图谱关系。\n")

            for index, (repo_url,) in enumerate(repos):
                print(f"[{index+1}/{total}] 分析: {repo_url} ...", end="")
                
                # 2. 调用 API 获取数据
                users = get_contributors_from_api(repo_url)
                
                if users:
                    # 3. 批量插入
                    sql_insert = """
                        INSERT INTO repo_contributors 
                        (repo_url, contributor_name, contributor_url, avatar_url)
                        VALUES (%s, %s, %s, %s)
                    """
                    data_values = [(repo_url, u['name'], u['url'], u['avatar']) for u in users]
                    
                    cursor.executemany(sql_insert, data_values)
                    conn.commit()
                    print(f" -> 存入 {len(users)} 位贡献者")
                else:
                    print(" -> 跳过")
                
                # API 免费版建议慢一点
                time.sleep(1.5)

    except Exception as e:
        print(f"\n发生错误: {e}")
    finally:
        conn.close()
        print("\n图谱数据构建完成。")

if __name__ == '__main__':
    main()