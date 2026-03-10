import requests
import json
import pymysql
import time
import urllib3

# 禁用 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# =========================
# 1. 配置区域
# =========================
API_KEY = "sk-78af31159c2a40738385e8cee354fd34"  # DeepSeek Key
API_URL = "https://api.deepseek.com/chat/completions"

# 【强烈建议】填入 GitHub Token，否则搜索极易被限流 (403错误)
# 申请地址: https://github.com/settings/tokens
GITHUB_TOKEN = "" 

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'lzz20050511', 
    'database': 'gitTrend_db',
    'charset': 'utf8mb4'
}

# =========================
# 2. 数据库操作函数
# =========================
def db_connect():
    return pymysql.connect(**DB_CONFIG)

def init_search_table():
    """
    初始化表结构：包含 search_prompt 列
    """
    conn = db_connect()
    try:
        with conn.cursor() as cursor:
            # 创建表 (如果不存在)
            sql = """
            CREATE TABLE IF NOT EXISTS ai_search_results (
                id INT AUTO_INCREMENT PRIMARY KEY,
                search_prompt TEXT COMMENT '用户的原始搜索需求',
                keyword VARCHAR(255) COMMENT 'AI提取的搜索关键词',
                repo VARCHAR(255) NOT NULL,
                url VARCHAR(255),
                description TEXT,
                lang VARCHAR(50),
                stars INT,
                ai_reason VARCHAR(500) COMMENT 'AI推荐理由',
                match_score INT COMMENT 'AI匹配分',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """
            cursor.execute(sql)
        conn.commit()
    except Exception as e:
        print(f" [DB Init Error] {e}")
    finally:
        conn.close()

def save_results_to_db(user_prompt, keyword, results):
    """
    将搜索结果追加保存到数据库
    """
    if not results:
        return 0

    # 确保表存在
    init_search_table()
    
    conn = db_connect()
    count = 0
    try:
        with conn.cursor() as cursor:
            sql = """
                INSERT INTO ai_search_results 
                (search_prompt, keyword, repo, url, description, lang, stars, ai_reason, match_score) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            data_list = []
            for item in results:
                data_list.append((
                    user_prompt,     # 存入用户的原始 Prompt
                    keyword,         # 存入提取的关键词
                    item['repo'],
                    item['url'],
                    item['description'],
                    item['lang'],
                    item['stars'],
                    item['reason'],
                    item['score']
                ))
            
            cursor.executemany(sql, data_list)
        conn.commit()
        count = len(data_list)
        print(f" >> [数据库] 已成功追加 {count} 条记录到 ai_search_results 表。")
    except Exception as e:
        print(f" >> [数据库保存失败] {e}")
        print("    (提示: 如果是列数不匹配错误，请尝试先 DROP TABLE ai_search_results)")
    finally:
        conn.close()
    return count

# =========================
# 3. 核心功能函数
# =========================
def get_headers():
    headers = {
        'Accept': 'application/vnd.github.v3+json',
        'User-Agent': 'Mozilla/5.0 (AI Project)',
    }
    if GITHUB_TOKEN:
        headers['Authorization'] = f'token {GITHUB_TOKEN}'
    return headers

def extract_keywords_with_ai(user_prompt):
    """步骤1: 用 AI 提取搜索关键词"""
    print(" >> 1. 正在分析需求并提取关键词...")
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "You are a search query optimizer. Extract the most important 1-2 keywords (english) from the user's description for searching GitHub. Just return the keywords separated by space, nothing else."},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.1
    }
    try:
        resp = requests.post(API_URL, json=payload, headers={"Authorization": f"Bearer {API_KEY}"}, verify=False)
        if resp.status_code == 200:
            kw = resp.json()['choices'][0]['message']['content'].strip()
            print(f"    -> 提取结果: [{kw}]")
            return kw
    except Exception as e:
        print(f"    -> AI 提取失败: {e}")
    return user_prompt

def search_github_candidates(keyword, limit=50):
    """步骤2: GitHub 广撒网搜索"""
    print(f" >> 2. 正在 GitHub 搜索 (Limit={limit})...")
    url = f"https://api.github.com/search/repositories?q={keyword}&sort=stars&order=desc&per_page={limit}"
    
    try:
        resp = requests.get(url, headers=get_headers(), verify=False, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            items = data.get('items', [])
            candidates = []
            for item in items:
                candidates.append({
                    "full_name": item['full_name'],
                    "html_url": item['html_url'],
                    "description": item['description'] if item['description'] else "No description",
                    "lang": item['language'],
                    "stars": item['stargazers_count']
                })
            print(f"    -> 找到 {len(candidates)} 个候选项目")
            return candidates
        elif resp.status_code == 403:
            print("    -> [错误] GitHub API 限流 (403)。请配置 Token 或稍后再试。")
        else:
            print(f"    -> [错误] API 状态码: {resp.status_code}")
        return []
    except Exception as e:
        print(f"    -> 搜索异常: {e}")
        return []

def ai_filter_repositories(user_requirement, candidates):
    """步骤3: AI 深度筛选"""
    if not candidates:
        return []
    
    print(" >> 3. 正在请求 DeepSeek 进行深度筛选 (请耐心等待)...")
    
    # 截取前 50 个，防止 Token 超出
    candidates = candidates[:50]
    candidate_str = json.dumps(candidates, ensure_ascii=False)
    
    system_prompt = """
    你是一个 GitHub 仓库高级筛选助手。
    用户的需求是：{user_requirement}
    
    下面是一个 JSON 列表。请根据用户的需求，**严格筛选**出最符合的仓库。
    
    筛选规则：
    1. 剔除与用户需求不相关的项目。
    2. 如果用户指定了语言，剔除其他语言。
    3. 优先保留 Stars 多且描述匹配的项目。
    
    请返回一个 JSON 对象，包含 "results" 列表，格式如下：
    {{
        "results": [
            {{
                "full_name": "owner/repo",
                "reason": "推荐理由（中文，一句话）",
                "match_score": 95
            }},
            ...
        ]
    }}
    请只返回纯 JSON 字符串，不要 Markdown 标记。
    """.format(user_requirement=user_requirement)

    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"候选仓库列表:\n{candidate_str}"}
        ],
        "temperature": 0.2,
        "response_format": { "type": "json_object" }
    }
    
    try:
        resp = requests.post(API_URL, json=payload, headers={"Authorization": f"Bearer {API_KEY}"}, verify=False, timeout=60)
        
        if resp.status_code == 200:
            content = resp.json()['choices'][0]['message']['content']
            # 清洗 Markdown
            content = content.replace("```json", "").replace("```", "").strip()
            
            ai_data = json.loads(content)
            result_list = ai_data.get('results', [])
            
            final_list = []
            candidate_map = {c['full_name']: c for c in candidates}
            
            for item in result_list:
                full_name = item.get('full_name')
                if full_name in candidate_map:
                    orig = candidate_map[full_name]
                    final_list.append({
                        "repo": full_name,
                        "url": orig['html_url'],
                        "stars": orig['stars'],
                        "lang": orig['lang'],
                        "description": orig['description'],
                        "reason": item.get('reason'),
                        "score": item.get('match_score')
                    })
            
            # 按分数降序
            final_list.sort(key=lambda x: x['score'], reverse=True)
            print(f"    -> 筛选完成，保留 {len(final_list)} 个最佳项目")
            return final_list
        else:
            print(f"    -> DeepSeek API 错误: {resp.text}")
            return []
    except Exception as e:
        print(f"    -> AI 筛选异常: {e}")
        return []

# =========================
# 4. 主程序入口 (命令行模式)
# =========================
def main():
    print("\n" + "="*50)
    print("   GitHub AI 智能搜索工具 (v2.0 数据库版)")
    print("="*50)
    
    # 1. 输入
    user_input = input("请输入搜索需求 (如: 找一个基于Vue3的后台管理模板): \n> ").strip()
    if not user_input:
        print("输入为空，退出。")
        return

    # 2. 提取关键词
    keyword = extract_keywords_with_ai(user_input)
    
    # 3. 搜索 GitHub
    candidates = search_github_candidates(keyword, limit=40)
    
    if not candidates:
        print("未找到任何候选项目。")
        return

    # 4. AI 筛选
    final_results = ai_filter_repositories(user_input, candidates)
    
    # 5. 展示与保存
    if final_results:
        print("\n" + "-"*50)
        print(f" 🎯 AI 为你推荐了 {len(final_results)} 个项目")
        print("-"*50)
        
        for res in final_results:
            print(f"[{res['score']}分] {res['repo']}")
            print(f"   理由: {res['reason']}")
            print(f"   URL : {res['url']}")
            print("." * 30)
            
        # 保存到数据库
        save_results_to_db(user_input, keyword, final_results)
        print("\n >> 全部流程结束，数据已入库。")
    else:
        print(" >> AI 认为候选列表中没有符合要求的项目。")

if __name__ == '__main__':
    main()