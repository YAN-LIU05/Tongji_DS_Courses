import requests
import json
import pymysql
import urllib3
import pandas as pd  # 引入 pandas 用于历史记录展示

# =========================
# 1. 配置区域
# =========================
API_KEY = "sk-"
API_URL = "https://api.deepseek.com/chat/completions"

# 【强烈建议】填写 Token，否则查用户 Repo 很容易 403
GITHUB_TOKEN = "" 

DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'lzz20050511', 
    'database': 'gitTrend_db',
    'charset': 'utf8mb4'
}

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# =========================
# 2. 数据库操作
# =========================
def db_connect():
    return pymysql.connect(**DB_CONFIG)

def init_author_table():
    """初始化作者分析表"""
    conn = db_connect()
    try:
        with conn.cursor() as cursor:
            sql = """
            CREATE TABLE IF NOT EXISTS ai_author_analysis (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(100) NOT NULL UNIQUE,
                avatar_url VARCHAR(255),
                bio TEXT,
                ai_report TEXT COMMENT 'AI生成的详细报告',
                tech_stack VARCHAR(255) COMMENT '技术栈标签',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """
            cursor.execute(sql)
        conn.commit()
    except Exception as e:
        print(f" [DB Init Error] {e}")
    finally:
        conn.close()

def save_analysis_to_db(user_info, ai_result):
    """保存或更新分析结果 (使用 INSERT ... ON DUPLICATE KEY UPDATE)"""
    init_author_table()
    conn = db_connect()
    try:
        with conn.cursor() as cursor:
            # 如果用户名已存在，则更新报告内容，而不是插入新行
            sql = """
                INSERT INTO ai_author_analysis 
                (username, avatar_url, bio, ai_report, tech_stack)
                VALUES (%s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                avatar_url = VALUES(avatar_url),
                bio = VALUES(bio),
                ai_report = VALUES(ai_report),
                tech_stack = VALUES(tech_stack);
            """
            cursor.execute(sql, (
                user_info['login'],
                user_info['avatar_url'],
                user_info.get('bio', ''),
                ai_result.get('report', '分析失败'),
                ai_result.get('stack', '')
            ))
        conn.commit()
        print(" >> [数据库] 作者画像已保存或更新。")
    except Exception as e:
        print(f" >> [数据库错误] {e}")
    finally:
        conn.close()

def get_history():
    conn = db_connect()
    try:
        df = pd.read_sql("SELECT username, tech_stack, created_at FROM ai_author_analysis ORDER BY updated_at DESC LIMIT 10", conn)
        return df
    except:
        return pd.DataFrame()
    finally:
        conn.close()

# =========================
# 3. GitHub API 抓取
# =========================
def get_headers():
    headers = {'Accept': 'application/vnd.github.v3+json'}
    if GITHUB_TOKEN:
        headers['Authorization'] = f'token {GITHUB_TOKEN}'
    return headers

def fetch_user_profile(username):
    """获取用户基本信息"""
    print(f" >> 1. 正在获取用户 {username} 的个人资料...")
    url = f"https://api.github.com/users/{username}"
    try:
        resp = requests.get(url, headers=get_headers(), verify=False)
        if resp.status_code == 200:
            print("    -> 成功获取资料。")
            return resp.json()
        elif resp.status_code == 404:
            print(f"    -> [错误] 找不到用户: {username} (404)")
        else:
            print(f"    -> [错误] API 状态码: {resp.status_code}")
    except Exception as e:
        print(f"    -> [网络错误] {e}")
    return None

def fetch_user_repos(username):
    """获取用户 Top 30 仓库"""
    print(" >> 2. 正在获取用户的公开仓库列表...")
    url = f"https://api.github.com/users/{username}/repos?sort=pushed&per_page=30&type=owner"
    try:
        resp = requests.get(url, headers=get_headers(), verify=False)
        if resp.status_code == 200:
            data = resp.json()
            simplified_repos = []
            for repo in data:
                if not repo['fork']: 
                    simplified_repos.append({
                        "name": repo['name'],
                        "desc": repo['description'],
                        "lang": repo['language'],
                        "stars": repo['stargazers_count'],
                        "updated": repo['updated_at'][:10]
                    })
            simplified_repos.sort(key=lambda x: x['stars'], reverse=True)
            result = simplified_repos[:20]
            print(f"    -> 成功获取 {len(result)} 个原创仓库。")
            return result
        else:
            print(f"    -> [错误] 获取仓库失败，状态码: {resp.status_code}")
            if resp.status_code == 403: print("       (提示: 可能是 GitHub API 限流，请配置 Token)")
    except Exception as e:
        print(f"    -> [网络错误] {e}")
    return []

# =========================
# 4. AI 分析逻辑
# =========================
def analyze_author_style(username, profile, repos):
    """调用 DeepSeek 生成画像"""
    if not repos:
        return {"report": "该用户没有公开的原创仓库，无法分析。", "stack": "无"}
        
    print(" >> 3. 正在请求 DeepSeek 生成能力画像 (请耐心等待)...")
    repo_str = json.dumps(repos, ensure_ascii=False)
    user_bio = profile.get('bio', '无')
    
    system_prompt = """
    你是一位资深的技术面试官和代码审计专家。请根据提供的 GitHub 用户简介和仓库列表，生成一份深度的【开发者能力画像】。
    分析维度：
    1. **核心技术栈**: 擅长的语言和框架。
    2. **擅长领域**: (如前端、后端、AI、系统底层、工具类等)。
    3. **代码/项目风格**: (如喜欢造轮子、注重文档、关注算法、还是偏向应用层)。
    4. **代表作分析**: 简要点评 1-2 个高星项目。
    5. **综合评价**: 用一段话总结该开发者的技术水平和特点。
    返回格式必须为 JSON: {"report": "详细的 Markdown 格式报告...", "stack": "Python, React, Rust (逗号分隔)"}
    """
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"用户名: {username}\n简介: {user_bio}\n仓库列表数据:\n{repo_str}"}
        ],
        "temperature": 0.3,
        "response_format": { "type": "json_object" }
    }

    try:
        resp = requests.post(API_URL, json=payload, headers={"Authorization": f"Bearer {API_KEY}"}, verify=False, timeout=60)
        if resp.status_code == 200:
            content = resp.json()['choices'][0]['message']['content']
            content = content.replace("```json", "").replace("```", "").strip()
            print("    -> AI 分析完成。")
            return json.loads(content)
    except Exception as e:
        print(f"    -> [AI 错误] {e}")
    
    return {"report": "AI 分析服务暂时不可用。", "stack": "未知"}

# =========================
# 5. 主程序入口 (命令行模式)
# =========================
def main():
    print("\n" + "="*50)
    print("   GitHub 作者能力画像生成器 (命令行版)")
    print("="*50)
    
    # 1. 获取输入
    username = input("请输入要分析的 GitHub 用户名 (例如: antfu): \n> ").strip()
    if not username:
        print("输入为空，程序退出。")
        return

    # 2. 抓取数据
    profile = fetch_user_profile(username)
    if not profile:
        return
        
    repos = fetch_user_repos(username)

    # 3. AI 分析
    analysis = analyze_author_style(username, profile, repos)

    # 4. 展示与保存
    if analysis and 'report' in analysis:
        print("\n" + "-"*50)
        print(" 📋 AI 生成的开发者画像报告")
        print("-"*50)
        print(f"**核心技术栈**: {analysis.get('stack', '未知')}\n")
        print(analysis['report'])
        
        # 保存到数据库
        save_analysis_to_db(profile, analysis)
    
    print("\n >> 流程结束。")

if __name__ == '__main__':
    main()