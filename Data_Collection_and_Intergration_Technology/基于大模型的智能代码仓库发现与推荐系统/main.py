import streamlit as st
import pymysql
import pandas as pd
from streamlit_echarts import st_echarts
# -----------------------------------------------------
# 新增引入美化菜单库 (需运行: pip install streamlit-option-menu)
from streamlit_option_menu import option_menu
# -----------------------------------------------------
import module_ai_search
import module_developer_profile
import module_chat_repo

# =========================
# 1. 页面配置
# =========================
st.set_page_config(
    page_title="GitHub 智能情报中心",
    page_icon="🚀",
    layout="wide"
)

# 注入自定义 CSS 以进一步美化侧边栏和整体布局
st.markdown("""
    <style>
        /* 侧边栏背景微调 */
        [data-testid="stSidebar"] {
            background-color: #f8f9fa;
        }
        /* 侧边栏标题样式 */
        .sidebar-title {
            font-size: 20px;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 10px;
            text-align: center;
        }
        .sidebar-subtitle {
            font-size: 12px;
            color: #7f8c8d;
            text-align: center;
            margin-bottom: 20px;
        }
        /* 调整主页面顶部留白 */
        .block-container {
            padding-top: 2rem;
        }
    </style>
""", unsafe_allow_html=True)

# =========================
# 2. 数据库连接函数
# =========================
def get_connection():
    return pymysql.connect(
        host='localhost',
        port=3306,
        user='root',
        password='lzz20050511',  # 记得提交作业时打码
        database='gitTrend_db',
        charset='utf8mb4'
    )

# =========================
# 3. 数据读取函数
# =========================
def load_trending_data():
    """读取热榜数据"""
    conn = get_connection()
    try:
        sql = """
        SELECT ranking, repo, lang, stars, forks, description, ai_summary, ai_tags, ai_score, url, readme 
        FROM github_trending_day 
        ORDER BY ranking ASC
        """
        df = pd.read_sql(sql, conn)
    except Exception:
        df = pd.DataFrame()
    finally:
        conn.close()
    return df

def load_graph_data():
    """读取图谱数据"""
    conn = get_connection()
    try:
        sql = "SELECT repo_url, contributor_name, avatar_url FROM repo_contributors LIMIT 50"
        df = pd.read_sql(sql, conn)
    except Exception:
        df = pd.DataFrame()
    finally:
        conn.close()
    return df

def load_search_history():
    """读取 AI 搜索历史"""
    conn = get_connection()
    try:
        sql = """
        SELECT id, search_prompt, repo, match_score, ai_reason, lang, stars, created_at 
        FROM ai_search_results 
        ORDER BY id DESC 
        LIMIT 50
        """
        df = pd.read_sql(sql, conn)
    except Exception:
        df = pd.DataFrame()
    finally:
        conn.close()
    return df

def load_author_history():
    """读取作者画像历史"""
    conn = get_connection()
    try:
        sql = """
        SELECT username, avatar_url, tech_stack, created_at, ai_report 
        FROM ai_author_analysis 
        ORDER BY updated_at DESC 
        LIMIT 20
        """
        df = pd.read_sql(sql, conn)
    except Exception:
        df = pd.DataFrame()
    finally:
        conn.close()
    return df

# =========================
# 4. 侧边栏导航 (已美化)
# =========================
with st.sidebar:
    # 顶部 Logo / 标题区域
    st.markdown('<div class="sidebar-title">🚀 GitHub 情报中心</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-subtitle">AI 驱动的开源洞察平台</div>', unsafe_allow_html=True)
    
    # 使用 option_menu 替代原生的 radio，样式更美观
    # options 列表中的字符串必须与下方逻辑判断完全一致
    page = option_menu(
        menu_title=None,  # 隐藏菜单标题
        options=[
            "📊 数据大屏", 
            "🤖 AI 深度分析", 
            "🕸️ 贡献者知识图谱", 
            "🔍 AI 智能搜库",
            "👨‍💻 作者深度画像",
            "💬 Chat with Repo"
        ],
        # 对应 Bootstrap 图标 (https://icons.getbootstrap.com/)
        icons=['bar-chart-fill', 'cpu', 'diagram-3-fill', 'search', 'person-bounding-box', 'chat-dots-fill'],
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "#fafafa"},
            "icon": {"color": "#6c757d", "font-size": "16px"}, 
            "nav-link": {"font-size": "14px", "text-align": "left", "margin": "5px", "--hover-color": "#eee"},
            "nav-link-selected": {"background-color": "#FF4B4B", "color": "white"}, # 选中颜色设为 Streamlit 红
        }
    )
    
    # 底部版权/信息区
    st.markdown("---")
    st.caption(f"📅 Database Status: Online")
    st.caption("Developed by Liu & Ji | 2026")

# 预加载基础数据
df_trend = load_trending_data()

# =========================
# 模块一：数据大屏
# =========================
if page == "📊 数据大屏":
    st.title("🔥 GitHub 今日热榜可视化")
    
    if df_trend.empty:
        st.warning("数据库为空，请先运行 new.py 抓取数据。")
    else:
        col1, col2, col3 = st.columns(3)
        col1.metric("今日项目数", len(df_trend))
        # 处理 stars 列可能包含 'k' 或 ',' 的情况，如果已经是清洗好的数字则无需处理
        try:
            max_stars = df_trend['stars'].astype(str).str.replace(',', '').astype(float).max()
        except:
            max_stars = 0
        col2.metric("最高 Star 数", int(max_stars))
        col3.metric("涉及编程语言", df_trend['lang'].nunique())
        
        st.divider()

        c1, c2 = st.columns([2, 1])
        with c1:
            st.subheader("🏆 Top 10 项目 Stars 对比")
            top10 = df_trend.head(10).copy()
            # 简单清洗用于绘图
            top10['stars_clean'] = top10['stars'].astype(str).str.replace(',', '').astype(float)
            st.bar_chart(top10.set_index('repo')['stars_clean'])
            
        with c2:
            st.subheader("🍩 语言分布")
            lang_counts = df_trend['lang'].value_counts()
            pie_data = [{"value": int(v), "name": k} for k, v in lang_counts.items()]
            options = {
                "tooltip": {"trigger": "item"},
                "series": [{"type": "pie", "radius": "70%", "data": pie_data}]
            }
            st_echarts(options=options, height="300px")

        st.subheader("📋 详细数据表")
        display_cols = ['ranking', 'repo', 'lang', 'stars', 'description']
        # 过滤掉不存在的列
        display_cols = [c for c in display_cols if c in df_trend.columns]
        st.dataframe(df_trend[display_cols])

# =========================
# 模块二：AI 深度分析
# =========================
elif page == "🤖 AI 深度分析":
    st.title("🧠 DeepSeek AI 项目解读")
    st.markdown("这里展示由 **DeepSeek API** 自动生成的项目摘要与评分。")
    
    if df_trend.empty:
        st.warning("暂无数据。")
    else:
        # 确保 ai_score 是数字
        df_trend['ai_score'] = pd.to_numeric(df_trend['ai_score'], errors='coerce').fillna(0)
        
        min_score = st.slider("筛选 AI 推荐分 >=", 0, 10, 7)
        filtered_df = df_trend[df_trend['ai_score'] >= min_score]
        
        for index, row in filtered_df.iterrows():
            summary = row['ai_summary'] if row['ai_summary'] else "暂无 AI 分析数据"
            tags = row['ai_tags'] if row['ai_tags'] else "无"
            score = int(row['ai_score'])
            
            with st.container():
                c1, c2 = st.columns([1, 4])
                with c1:
                    st.metric(label="AI 推荐分", value=f"{score}/10")
                with c2:
                    st.markdown(f"### [{row['repo']}]({row['url']})")
                    st.info(f"💡 **AI 摘要**: {summary}")
                    st.caption(f"🏷️ 技术栈: {tags}")
                st.divider()

# =========================
# 模块三：知识图谱
# =========================
elif page == "🕸️ 贡献者知识图谱":
    st.title("🕸️ 开源贡献关系图谱")
    st.markdown("展示 **项目 (绿色)** 与 **贡献者 (蓝色)** 之间的协作关系。")
    
    df_graph = load_graph_data()
    
    if df_graph.empty:
        st.warning("数据库中没有图谱数据，请先运行 new3.py (crawl_graph_api)")
    else:
        nodes = []
        links = []
        seen_nodes = set()
        
        for _, row in df_graph.iterrows():
            repo_name = row['repo_url'].split('/')[-1]
            user_name = row['contributor_name']
            
            if repo_name not in seen_nodes:
                nodes.append({"name": repo_name, "symbolSize": 20, "itemStyle": {"color": "#4caf50"}, "category": 0})
                seen_nodes.add(repo_name)
            
            if user_name not in seen_nodes:
                nodes.append({"name": user_name, "symbolSize": 10, "itemStyle": {"color": "#2196f3"}, "category": 1})
                seen_nodes.add(user_name)
                
            links.append({"source": user_name, "target": repo_name})
            
        option = {
            "tooltip": {},
            "legend": [{"data": ["项目", "贡献者"]}],
            "series": [
                {
                    "type": "graph",
                    "layout": "force",
                    "symbolSize": 15,
                    "roam": True,
                    "label": {"show": True, "position": "right"},
                    "force": {"repulsion": 1000, "edgeLength": 50},
                    "data": nodes,
                    "links": links,
                    "categories": [{"name": "项目"}, {"name": "贡献者"}]
                }
            ]
        }
        st_echarts(options=option, height="600px")

# =========================
# 模块四：AI 智能搜库
# =========================
elif page == "🔍 AI 智能搜库":
    st.title("🔍 AI 智能仓库猎手")
    st.markdown("告别简单的关键词搜索！告诉 DeepSeek 你想找什么，它会为你筛选并**存入数据库**。")
    
    with st.form("search_form"):
        user_input = st.text_area("请输入你的需求 (Prompt):", height=100, placeholder="例如：找一些用 Python 写的量化回测框架")
        c1, c2 = st.columns([1, 1])
        with c1:
            search_limit = st.number_input("抓取候选数量", min_value=10, max_value=80, value=30)
        with c2:
            submitted = st.form_submit_button("🚀 开始 AI 搜索")

    if submitted and user_input:
        st.divider()
        status_box = st.status("正在执行智能搜索任务...", expanded=True)
        
        status_box.write("1️⃣ 提取关键词...")
        search_keyword = module_ai_search.extract_keywords_with_ai(user_input)
        status_box.write(f"   -> 关键词: **{search_keyword}**")
        
        status_box.write(f"2️⃣ GitHub 检索 Top {search_limit}...")
        candidates = module_ai_search.search_github_candidates(search_keyword, limit=search_limit)
        
        if not candidates:
            status_box.update(label="❌ GitHub 无结果", state="error")
            st.error("无法获取候选列表。")
        else:
            status_box.write("3️⃣ DeepSeek 正在筛选...")
            final_results = module_ai_search.ai_filter_repositories(user_input, candidates)
            
            if final_results:
                status_box.write("4️⃣ 存入数据库...")
                save_count = module_ai_search.save_results_to_db(user_input, search_keyword, final_results)
                status_box.update(label=f"✅ 完成！已存 {save_count} 条。", state="complete")
                
                st.success(f"🎉 找到 {len(final_results)} 个匹配项目")
                for res in final_results:
                    with st.expander(f"[{res['score']}分] {res['repo']} ({res['lang']})", expanded=True):
                        st.markdown(f"**理由**: {res['reason']}")
                        st.markdown(f"**简介**: {res['description']}")
                        st.markdown(f"⭐ {res['stars']} | [链接]({res['url']})")
            else:
                status_box.update(label="⚠️ AI 未找到合适项目", state="complete")

    st.divider()
    st.subheader("📜 历史搜索记录")
    df_history = load_search_history()
    if not df_history.empty:
        st.dataframe(df_history, use_container_width=True)
    else:
        st.info("暂无记录")

# =========================
# 模块五：作者深度画像
# =========================
elif page == "👨‍💻 作者深度画像":
    st.title("👨‍💻 GitHub 开发者能力画像")
    st.markdown("输入一个 GitHub ID，AI 将通过分析其代码库，生成一份**技术能力评估报告**。")

    # 1. 输入区
    c1, c2 = st.columns([3, 1])
    with c1:
        target_user = st.text_input("请输入 GitHub 用户名 (例如: torvalds, antfu)", placeholder="输入 ID 回车")
    with c2:
        st.write("") # 占位
        btn_analyze = st.button("🚀 生成画像", type="primary")

    # 2. 分析逻辑
    if btn_analyze and target_user:
        st.divider()
        
        col_info, col_report = st.columns([1, 3])
        
        with col_info:
            with st.status("正在抓取数据...", expanded=True) as status:
                # A. 获取头像和简介
                status.write("🔍 查找用户...")
                profile = module_developer_profile.fetch_user_profile(target_user)
                
                if not profile:
                    status.update(label="❌ 用户不存在", state="error")
                    st.error(f"找不到用户: {target_user}")
                    st.stop()
                
                st.image(profile['avatar_url'], width=150)
                st.markdown(f"**{profile.get('name', target_user)}**")
                st.caption(f"📍 {profile.get('location', '未知')}")
                st.info(profile.get('bio', '这家伙很懒，没有简介'))
                
                # B. 获取仓库
                status.write("📦 获取仓库列表...")
                repos = module_developer_profile.fetch_user_repos(target_user)
                status.write(f"✅ 获取到 {len(repos)} 个原创仓库")
                
                # C. AI 分析
                status.write("🧠 DeepSeek 正在分析...")
                analysis = module_developer_profile.analyze_author_style(target_user, profile, repos)
                
                # D. 存库
                status.write("💾 正在归档...")
                module_developer_profile.save_analysis_to_db(profile, analysis)
                
                status.update(label="✨ 画像生成完毕", state="complete")

        with col_report:
            st.subheader("📋 AI 深度评估报告")
            
            # 展示技术栈
            tags = analysis.get('stack', '').split(',')
            st.write("🛠️ **核心技术栈**:")
            st.write(" ".join([f"`{t.strip()}`" for t in tags]))
            
            st.divider()
            
            # 展示报告
            report_text = analysis.get('report', '')
            st.markdown(report_text)
            
            # 可视化：语言分布
            if repos:
                st.divider()
                st.caption("📊 仓库语言构成 (Top 20)")
                lang_data = {}
                for r in repos:
                    l = r['lang'] if r['lang'] else 'Other'
                    lang_data[l] = lang_data.get(l, 0) + 1
                
                pie_data = [{"value": v, "name": k} for k, v in lang_data.items()]
                st_echarts(options={
                    "tooltip": {"trigger": "item"},
                    "series": [{"type": "pie", "radius": ["40%", "70%"], "data": pie_data}]
                }, height="250px")

    # 3. 历史记录
    st.divider()
    st.subheader("🗂️ 历史画像库")
    df_history = load_author_history()
    
    if not df_history.empty:
        for idx, row in df_history.iterrows():
            with st.expander(f"{row['username']} - {row['tech_stack']}"):
                c_img, c_txt = st.columns([1, 5])
                with c_img:
                    st.image(row['avatar_url'], width=60)
                with c_txt:
                    st.markdown(row['ai_report'])
                    st.caption(f"生成时间: {row['created_at']}")
    else:
        st.info("暂无历史画像，快去生成一个吧！")

# =========================
# 模块六：Chat with Repo (RAG)
# =========================
elif page == "💬 Chat with Repo":
    st.title("💬 与项目文档对话 (RAG)")
    st.markdown("基于 **向量数据库** 和 **DeepSeek**，实现对 README 的精准问答。")

    # 1. 获取所有有 README 的项目列表
    # 我们从 github_trending_day 表中获取有 readme 的项目
    # 注意：df_trend 在页面开头已经加载过，但最好重新查一次确保状态
    repo_list = []
    if 'readme' in df_trend.columns:
        # 筛选出 readme 不为空的项目
        has_readme = df_trend[df_trend['readme'].notnull() & (df_trend['readme'] != '')]
        repo_list = has_readme['repo'].tolist()

    if not repo_list:
        st.error("数据库中没有带 README 的项目。请先运行 new1.py 抓取 README。")
    else:
        # 2. 选择项目
        selected_repo = st.selectbox("选择一个项目开始对话:", repo_list)

        # 3. 初始化/索引检查
        # 使用 session_state 记录当前项目，避免每次刷新都重做 embedding
        if "current_repo" not in st.session_state:
            st.session_state.current_repo = None
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # 如果切换了项目，清空聊天记录并重新索引
        if st.session_state.current_repo != selected_repo:
            st.session_state.current_repo = selected_repo
            st.session_state.messages = [] # 清空聊天记录
            
            with st.spinner(f"正在读取并索引 {selected_repo} 的文档..."):
                readme_text = module_chat_repo.get_readme_from_mysql(selected_repo)
                if readme_text:
                    module_chat_repo.index_repo(selected_repo, readme_text)
                    st.success(f"{selected_repo} 索引加载完成！")
                else:
                    st.warning("该项目数据库中 README 为空，无法对话。")

        # 4. 聊天界面
        # 显示历史消息
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # 接收用户输入
        if prompt := st.chat_input(f"问问关于 {selected_repo} 的问题..."):
            # 显示用户消息
            st.chat_message("user").markdown(prompt)
            st.session_state.messages.append({"role": "user", "content": prompt})

            # 调用 RAG 引擎
            with st.spinner("AI 正在检索文档并思考..."):
                ai_response = module_chat_repo.query_deepseek_rag(selected_repo, prompt)

            # 显示 AI 回复
            with st.chat_message("assistant"):
                st.markdown(ai_response)
            st.session_state.messages.append({"role": "assistant", "content": ai_response})