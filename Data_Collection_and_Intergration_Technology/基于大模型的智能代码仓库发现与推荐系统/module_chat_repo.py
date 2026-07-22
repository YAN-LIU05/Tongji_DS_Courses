import chromadb
from chromadb.utils import embedding_functions
from sentence_transformers import SentenceTransformer
import requests
import json
import pymysql

# =========================
# 配置
# =========================
# DeepSeek 配置
API_KEY = "sk-" # 记得换回你的 Key
API_URL = "https://api.deepseek.com/chat/completions"

# 数据库配置 (读取 README 用)
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'lzz20050511',
    'database': 'gitTrend_db',
    'charset': 'utf8mb4'
}

# =========================
# RAG 引擎初始化
# =========================
print("正在初始化向量模型 (首次运行会下载模型，约 80MB)...")
# 使用本地轻量级模型，完全免费，无需调用 OpenAI Embedding API
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

# 初始化 ChromaDB (持久化存储到本地文件夹 ./chroma_db)
chroma_client = chromadb.PersistentClient(path="./chroma_db")

# 创建或获取集合
collection = chroma_client.get_or_create_collection(name="repo_readmes")

# =========================
# 工具函数
# =========================

def get_readme_from_mysql(repo_name):
    """从 MySQL 获取 README 原始内容"""
    conn = pymysql.connect(**DB_CONFIG)
    try:
        with conn.cursor() as cursor:
            # 优先查 github_trending_day
            sql = "SELECT readme FROM github_trending_day WHERE repo = %s"
            cursor.execute(sql, (repo_name,))
            res = cursor.fetchone()
            if res and res[0]:
                return res[0]
            
            # 如果没有，尝试查 search_results 表 (兼容 new5.py 的数据)
            # 注意：new5.py 存的是 'description' 比较短，最好还是要有完整 README
            # 这里为了演示，仅查 trending 表
            return None
    finally:
        conn.close()

def chunk_text(text, chunk_size=500, overlap=50):
    """将长文本切分为小段"""
    if not text:
        return []
    
    chunks = []
    start = 0
    text_len = len(text)
    
    while start < text_len:
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start += (chunk_size - overlap) # 重叠切片，防止上下文丢失
        
    return chunks

def index_repo(repo_name, readme_text):
    """
    建立索引：将 README 切片 -> 向量化 -> 存入 ChromaDB
    """
    # 1. 检查是否已经存在 (避免重复索引)
    existing = collection.get(where={"repo": repo_name})
    if existing['ids']:
        return True # 已经索引过了

    print(f" >> [RAG] 正在构建索引: {repo_name} ...")
    
    # 2. 文本切片
    chunks = chunk_text(readme_text)
    if not chunks:
        return False
        
    # 3. 生成 ID 和 Metadata
    ids = [f"{repo_name}_{i}" for i in range(len(chunks))]
    metadatas = [{"repo": repo_name} for _ in range(len(chunks))]
    
    # 4. 生成向量
    # SentenceTransformer 可以批量生成
    embeddings = embedding_model.encode(chunks).tolist()
    
    # 5. 存入 Chroma
    collection.add(
        documents=chunks,
        embeddings=embeddings,
        metadatas=metadatas,
        ids=ids
    )
    print(f" >> [RAG] 索引完成，存入 {len(chunks)} 个片段。")
    return True

def query_deepseek_rag(repo_name, user_question):
    """
    RAG 核心流程：检索 -> 组装 Prompt -> 提问 DeepSeek
    """
    # 1. 将用户问题向量化
    query_vec = embedding_model.encode([user_question]).tolist()
    
    # 2. 在 Chroma 中检索最相关的 3 个片段
    results = collection.query(
        query_embeddings=query_vec,
        n_results=3,
        where={"repo": repo_name} # 限定只在当前仓库里找
    )
    
    # 提取文本内容
    context_chunks = results['documents'][0]
    context_text = "\n\n".join(context_chunks)
    
    # 3. 组装 Prompt
    system_prompt = f"""
    你是一个开源项目技术支持助手。
    用户正在询问关于项目 "{repo_name}" 的问题。
    
    请利用下面的【参考文档】内容来回答用户。
    如果参考文档中没有相关信息，请诚实地说“文档中未找到相关信息”，不要编造。
    
    【参考文档】:
    {context_text}
    """
    
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_question}
        ],
        "temperature": 0.2
    }
    
    # 4. 调用 API
    try:
        resp = requests.post(API_URL, json=payload, headers={"Authorization": f"Bearer {API_KEY}"})
        if resp.status_code == 200:
            return resp.json()['choices'][0]['message']['content']
        else:
            return f"API Error: {resp.text}"
    except Exception as e:
        return f"Request Error: {e}"