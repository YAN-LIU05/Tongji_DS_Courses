import pymysql
import requests
import json
import time
import re

# =========================
# 配置
# =========================
API_KEY = "sk-"  # 【注意】这里填入你的新 Key
API_URL = "https://api.deepseek.com/chat/completions"

DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'lzz20050511',  # 记得提交作业时打码
    'database': 'gitTrend_db',
    'charset': 'utf8mb4'
}

def db_connect():
    return pymysql.connect(**DB_CONFIG)

def call_deepseek_analysis(readme_content):
    """
    调用 DeepSeek API 分析文本
    """
    # 截取前 3000 个字符，防止 Token 超出限制或花费太多
    # 通常项目的核心介绍都在开头
    content_snippet = readme_content[:3000]

    # 构造 Prompt (提示词)
    # 强制要求返回 JSON 格式，方便代码解析
    system_prompt = """
    你是一个开源项目技术分析师。请根据用户提供的 GitHub README 内容，进行以下分析：
    1. summary: 用中文一句话概括这个项目是做什么的（不超过50字）。
    2. tags: 提取项目涉及的核心编程语言或技术栈（不超过5个，英文逗号分隔）。
    3. score: 根据文档完整度和项目有趣程度，给出一个推荐分数（1-10的整数）。
    
    请务必只返回标准的 JSON 格式，不要包含 Markdown 标记（如 ```json）。
    格式示例：
    {"summary": "一个基于Python的爬虫框架", "tags": "Python, Web, Crawler", "score": 8}
    """

    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"README内容如下:\n{content_snippet}"}
        ],
        "temperature": 0.3, # 温度低一点，输出更稳定
        "response_format": { "type": "json_object" } # 强制 JSON 模式（如果模型支持）
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            # 获取 AI 回复的内容
            ai_text = result['choices'][0]['message']['content']
            # 清洗一下可能的 markdown 符号
            ai_text = ai_text.replace("```json", "").replace("```", "").strip()
            return json.loads(ai_text)
        else:
            print(f"  [API Error] Status: {response.status_code}, Msg: {response.text}")
            return None
    except Exception as e:
        print(f"  [Request Error] {e}")
        return None

def main():
    conn = db_connect()
    if not conn:
        print("数据库连接失败")
        return

    try:
        with conn.cursor() as cursor:
            # 1. 查找有 README 内容，但是还没有 AI 分析结果（ai_summary 为空）的记录
            print("正在查询待分析的数据...")
            sql_select = """
                SELECT repo, readme 
                FROM github_trending_day 
                WHERE readme IS NOT NULL 
                  AND readme != '' 
                  AND ai_summary IS NULL
            """
            cursor.execute(sql_select)
            tasks = cursor.fetchall()
            
            total = len(tasks)
            print(f"发现 {total} 个项目等待 AI 分析。\n")

            for index, (repo, readme) in enumerate(tasks):
                print(f"[{index+1}/{total}] 正在分析: {repo} ...")
                
                # 2. 调用 DeepSeek
                analysis_result = call_deepseek_analysis(readme)

                if analysis_result:
                    summary = analysis_result.get('summary', '暂无介绍')
                    tags = analysis_result.get('tags', '')
                    score = analysis_result.get('score', 0)

                    print(f"  -> 评分: {score} | 标签: {tags}")
                    print(f"  -> 摘要: {summary}")

                    # 3. 更新数据库
                    sql_update = """
                        UPDATE github_trending_day 
                        SET ai_summary = %s, ai_tags = %s, ai_score = %s
                        WHERE repo = %s
                    """
                    cursor.execute(sql_update, (summary, tags, score, repo))
                    conn.commit()
                    print("  -> [保存成功]")
                else:
                    print("  -> [分析失败，跳过]")
                
                # 稍微休眠一下，避免触发 API 速率限制
                time.sleep(1)

    except Exception as e:
        print(f"\n发生错误: {e}")
    finally:
        conn.close()
        print("\n分析任务结束。")

if __name__ == '__main__':
    main()