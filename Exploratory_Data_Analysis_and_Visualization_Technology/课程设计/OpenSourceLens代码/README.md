# OpenSourceLens：开源项目智能可视化分析平台

OpenSourceLens 是一个基于 Reflex 的中文交互式数据可视化平台，用于分析 GitHub 开源项目的热度、活跃度、健康度、国际化、机器学习聚类、异常检测和文本语义特征。

## 功能列表

- 首页总览：项目总数、Stars、Forks、贡献者、健康度、活跃度和核心图表。
- 项目详情：单项目基础指标、雷达图、Issue 类型、贡献者地域和核心指标解读。
- 项目对比：多项目评分对比、雷达对比、表格和结构差异分析。
- 地域可视化：国家分布、城市气泡、国家 Top、城市 Top、项目-国家热力图。
- 统计分布与相关性：指标分布、箱线图、语言分组评分、相关性热力图。
- 时间序列趋势：历史快照趋势、非零变化排行和趋势对比。
- 机器学习分析：K-Means 聚类、PCA 降维、Isolation Forest 异常检测。
- 文本语义分析：README 语义嵌入、项目相似度、Issue 主题、Commit 类型。
- GitHub Trending 实时榜：按钮触发采集 Trending，展示排名、仓库、语言、Stars、Forks、简介和 URL。
- Stars 实时榜：按钮触发查询 GitHub 当前 Stars 排名，展示仓库、语言、Stars、Forks、简介和 URL。

## 技术栈

- Reflex
- pandas / numpy
- Plotly
- scikit-learn
- joblib
- requests / python-dotenv

不使用 Streamlit、React 或 JavaScript。

## 目录结构

```text
.
├── AGENTS.md
├── README.md
├── pyproject.toml
├── requirements.txt
├── rxconfig.py
├── data/
│   ├── raw/
│   └── processed/
├── models/
├── scripts/
│   ├── collect_github_data.py
│   ├── clean_data.py
│   ├── run_pipeline.py
│   ├── update_loop.py
│   ├── generate_demo_data.py
│   ├── build_features.py
│   ├── build_star_growth.py
│   ├── train_models.py
│   └── build_text_features.py
└── opensource_lens/
    ├── opensource_lens.py
    ├── state.py
    ├── components/
    ├── pages/
    └── utils/
```

## 安装

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Windows PowerShell：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 运行步骤

请按顺序执行，先生成或采集数据，再构建页面依赖的数据产物。真实 GitHub 数据推荐配置 `GITHUB_TOKEN`，否则容易遇到 API 频率限制。

```bash
cp .env.example .env
# 在 .env 中填写 GITHUB_TOKEN
python scripts/collect_github_data.py
python scripts/clean_data.py
python scripts/build_features.py
python scripts/build_star_growth.py
python scripts/train_models.py
python scripts/build_text_features.py
reflex run
```

如果只想快速演示，可以使用 demo 数据：

```bash
python scripts/generate_demo_data.py
python scripts/clean_data.py
python scripts/build_features.py
python scripts/build_star_growth.py
python scripts/train_models.py
python scripts/build_text_features.py
reflex run
```

## 真实 GitHub 数据采集

`scripts/collect_github_data.py` 默认会先通过 GitHub Search API 自动发现最近活跃的真实仓库，再通过 GitHub API 采集项目数据。`data/project_list.txt` 只作为发现数量不足或需要固定种子项目时的补充，不再限制采集范围。

- 仓库基础信息：Stars、Forks、Watchers、Open Issues、语言、License、Topics。
- 近期活动：Commit、Issue、Pull Request。
- 贡献者：贡献数、公开 profile 中的 location 字段。
- README 文本：用于文本语义分析。

采集结果会写入：

- `data/raw/github_snapshot.json`
- `data/processed/repos.csv`
- `data/processed/scores.csv`
- `data/processed/contributors.csv`
- `data/processed/geo_contributors.csv`
- `data/processed/issues.csv`
- `data/processed/pulls.csv`
- `data/processed/text_corpus.csv`
- `data/processed/refresh_metadata.json`

默认采集真实 GitHub 数据：

```bash
python scripts/collect_github_data.py --days 90 --contributors 20 --items 30 --sleep 1
```

完整更新前端会读取的数据、特征、模型和文本结果：

```bash
python scripts/run_pipeline.py --source github --discover-target 220
```

如果要按自己的 GitHub Search 条件查询真实仓库，可以传入 `--search-query`，并且可以重复传入多个查询：

```bash
python scripts/run_pipeline.py --source github --discover-target 120 --search-query "topic:visualization stars:>100 pushed:>=2026-01-01" --search-query "language:Python topic:dashboard stars:>50"
```

若确实只想采集 `data/project_list.txt` 中的固定列表：

```bash
python scripts/collect_github_data.py --seed-only
```

如果当前网络连接 GitHub 不稳定，可以降低采集量并放慢请求：

```bash
python scripts/collect_github_data.py --contributors 10 --items 20 --sleep 2
```

采集脚本会对 SSL、连接中断、超时和 5xx 错误进行重试。某个仓库多次失败时，默认会跳过该仓库、继续采集后续仓库，并在 `data/processed/refresh_metadata.json` 中记录失败仓库。若希望任一仓库失败就立即中断，可加：

```bash
python scripts/collect_github_data.py --strict
```

脚本默认支持断点续采：每成功采集一个仓库就会写入 `data/raw/github_snapshot.json` 和 `data/processed/`，下次运行会跳过已经采集过的仓库，不会删除已有结果。若要强制重新采集已有仓库：

```bash
python scripts/collect_github_data.py --refresh-existing
```

若确实要完全重建采集输出：

```bash
python scripts/collect_github_data.py --no-resume
```

注意：该脚本只在命令行运行，不会在 Reflex 页面渲染时调用 GitHub API。

采集和流水线完成后，前端无需重新写页面。启动或刷新 Reflex 应用时会读取 `data/processed/`；如果应用已经打开，点击页面右上角“刷新本地数据”，新爬到的仓库会进入首页表格、项目详情选择器、对比页、地域页、机器学习页和文本页。

## Demo 数据生成

`scripts/generate_demo_data.py` 会在 `data/processed/` 下生成：

- `repos.csv`
- `scores.csv`
- `contributors.csv`
- `geo_contributors.csv`
- `issues.csv`
- `pulls.csv`
- `text_results.csv`

Demo 数据包含 PyTorch、TensorFlow、Transformers、scikit-learn、pandas、NumPy、LangChain、Ray、Spark、Elasticsearch 等 20 个项目。

## 清洗数据

`scripts/clean_data.py` 会统一字段、补齐缺失列、标准化日期，并保持 `repos.csv` 和 `scores.csv` 结构一致。

```bash
python scripts/clean_data.py
```

## 特征工程

`scripts/build_features.py` 会读取 `repos.csv` 和 `geo_contributors.csv`，生成：

- 热度评分 `popularity_score`
- 活跃度评分 `activity_score`
- 健康度评分 `health_score`
- 国际化评分 `globalization_score`

所有评分范围为 0 到 1。

## GitHub Trending 实时榜

`/growth` 页面用于实时展示 GitHub Trending：

- 实时查询：在页面点击“实时刷新 Trending”后，系统会采集 GitHub Trending 页面，展示排名、仓库名、语言、Stars、Forks、周期新增 Stars、简介、URL 和采集时间。
- 触发方式：该请求只在点击按钮时发生，不会在页面渲染时自动调用 GitHub，也不会局限于本地 CSV 中已有的项目。

实时查询支持按 GitHub Trending 的语言和时间范围筛选。该页面不再逐仓库调用 stargazers API，因此点击后应在一次 Trending 页面请求完成后直接更新前端。

## Stars 实时榜

`/stars` 页面用于实时展示 GitHub 当前 Stars 排名：

- 实时查询：在页面点击“实时查询 Stars 榜”后，系统调用 GitHub Search API，按 Stars 降序返回仓库。
- 展示字段：排名、仓库名、语言、Stars、Forks、Open Issues、简介、URL、更新时间、最近 Push、查询时间。
- 触发方式：该请求只在点击按钮时发生，不会在页面渲染时自动调用 GitHub，也不会读取本地项目列表。

离线真实数据流水线仍会把当前 Stars 写入 `data/processed/star_history.csv`。随后运行：

```bash
python scripts/build_star_growth.py
```

会生成：

- `data/processed/star_growth.csv`

其中包含：

- `growth_30m`：30 分钟内 Stars 增长。
- `growth_24h`：24 小时内 Stars 增长。

增长排行需要至少两次不同时间的采集快照。推荐用 `update_loop.py` 每 30 分钟自动采集一次。

## 机器学习训练

`scripts/train_models.py` 会读取 `data/processed/scores.csv`，训练并输出：

- `data/processed/ml_results.csv`
- `models/scaler.pkl`
- `models/kmeans.pkl`
- `models/pca.pkl`
- `models/isolation_forest.pkl`

模型包括 K-Means、PCA 和 Isolation Forest。异常原因使用规则模板生成，便于课程展示解释。

模型是提前离线训练好的。Reflex 页面只读取 `ml_results.csv` 和 `models/` 下的训练产物，不会在页面渲染时训练模型。

## 文本分析

`scripts/build_text_features.py` 会生成 `data/processed/text_results.csv`。如果安装了 `sentence-transformers`，会优先使用语义嵌入；如果没有安装，会自动退化为 TF-IDF，不影响页面运行。

如果存在真实采集产生的 `text_corpus.csv`，文本分析会优先使用 README、Topics 和描述字段；否则使用 `scores.csv` 中的描述和标签。

## 一键流水线

真实 GitHub 数据完整流水线：

```bash
python scripts/run_pipeline.py --source github
```

默认真实流水线会尝试扩展到约 220 个最近活跃项目。若只想使用 `data/project_list.txt` 中的种子项目：

```bash
python scripts/run_pipeline.py --source github --discover-target 0
```

Demo 数据完整流水线：

```bash
python scripts/run_pipeline.py --source demo
```

只更新数据和评分、不重训模型：

```bash
python scripts/run_pipeline.py --source github --skip-train
```

## 定期更新与手动重训

推荐策略：

- GitHub 数据和特征：每 1 到 6 小时更新一次。
- 文本特征：每次数据更新后生成。
- 机器学习模型：每天或每次课程展示前手动重训一次。

长期运行更新循环：

```bash
python scripts/update_loop.py --source github --interval-minutes 60 --train-every 24
```

含义：

- 每 60 分钟采集一次真实 GitHub 数据并更新特征、Stars 历史快照、文本结果。
- 每 24 次更新重训一次模型。
- 非重训轮次只更新数据、特征和文本，不覆盖模型文件。

如果要让 30 分钟增长榜更准确，建议：

```bash
python scripts/update_loop.py --source github --interval-minutes 30 --train-every 48 --discover-target 220
```

如果希望完全手动重训：

```bash
python scripts/run_pipeline.py --source github --skip-train
python scripts/train_models.py
python scripts/build_text_features.py
```

也可以使用系统计划任务，例如 Linux/macOS cron：

```cron
0 * * * * cd /path/to/project && . .venv/bin/activate && python scripts/run_pipeline.py --source github --skip-train
0 2 * * * cd /path/to/project && . .venv/bin/activate && python scripts/train_models.py && python scripts/build_text_features.py
```

Windows 可以用“任务计划程序”创建相同命令。

## 平台刷新机制

平台启动时会通过 `on_mount` 读取 `data/processed/` 下的 CSV 和 `refresh_metadata.json`。

平台运行过程中：

- 外部定时脚本或手动命令负责更新真实 GitHub 数据、特征和模型结果。
- 页面顶部的“刷新本地数据”按钮会检测本地 processed 文件是否变化。
- 如果文件变化，平台会重新加载 CSV 和模型结果摘要。
- 页面不会直接调用 GitHub API，也不会在页面渲染时训练模型。

## 页面说明

- `/`：首页总览。
- `/project`：项目详情。
- `/compare`：项目对比。
- `/geo`：地域可视化。
- `/statistics`：统计分布与相关性。
- `/trends`：时间序列趋势。
- `/growth`：GitHub Trending 实时榜。
- `/stars`：Stars 实时榜。
- `/ml`：机器学习分析。
- `/text`：文本语义分析。

Reflex 页面只读取 `data/processed/` 下的数据，不在页面渲染时爬取 GitHub，也不在页面渲染时训练模型。

## 数据限制

如果使用真实 GitHub 数据，结果取决于 GitHub API 可访问性、Token 权限、频率限制以及采集时刻。若使用 demo 数据，则仅适合课程展示和功能验证，不代表实时 GitHub 状态。

贡献者地域数据来自 GitHub 用户公开 profile 中的 location 字段，可能存在缺失、模糊、不准确或虚构情况，因此地域分析结果仅作为近似参考。

## 未来改进

- 增加导出课程报告和图表截图功能。
- 增加更细的 Issue/PR 时间序列趋势页面。
- 增加更多模型评估与聚类解释指标。
