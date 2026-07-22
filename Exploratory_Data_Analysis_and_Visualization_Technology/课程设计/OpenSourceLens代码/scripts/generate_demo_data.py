from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np
import pandas as pd


OUT_DIR = Path("data/processed")
NOW = datetime.now(timezone.utc)

PROJECTS = [
    ("pytorch/pytorch", "PyTorch", "面向研究与生产的深度学习框架", "Python", "BSD-3-Clause", 89000, 24800, 2100, 5400, 3900, 2450, 980, 1120, 0.78, 0.71, 12, 23, "deep-learning;gpu;tensor"),
    ("tensorflow/tensorflow", "TensorFlow", "Google 开源的机器学习平台", "C++", "Apache-2.0", 187000, 74600, 8400, 3300, 3700, 1380, 720, 640, 0.74, 0.66, 11, 20, "machine-learning;serving;neural-network"),
    ("huggingface/transformers", "Transformers", "主流 Transformer 模型与训练推理接口", "Python", "Apache-2.0", 145000, 28600, 1200, 1700, 2800, 1960, 820, 940, 0.81, 0.77, 10, 18, "nlp;llm;transformer"),
    ("scikit-learn/scikit-learn", "scikit-learn", "经典机器学习算法库", "Python", "BSD-3-Clause", 62000, 26000, 1500, 1900, 2600, 430, 240, 280, 0.85, 0.78, 9, 16, "machine-learning;classification;regression"),
    ("pandas-dev/pandas", "pandas", "结构化数据分析与时间序列工具", "Python", "BSD-3-Clause", 45000, 18500, 780, 3600, 3100, 650, 390, 420, 0.82, 0.80, 9, 17, "dataframe;analytics;timeseries"),
    ("numpy/numpy", "NumPy", "Python 科学计算基础库", "Python", "BSD-3-Clause", 30000, 11000, 650, 1450, 1700, 520, 210, 260, 0.86, 0.82, 8, 15, "array;scientific-computing;linear-algebra"),
    ("keras-team/keras", "Keras", "高层神经网络 API", "Python", "Apache-2.0", 61000, 19600, 1600, 420, 1200, 360, 160, 190, 0.79, 0.70, 7, 12, "deep-learning;api;modeling"),
    ("langchain-ai/langchain", "LangChain", "LLM 应用、Agent 与 RAG 开发框架", "Python", "MIT", 96000, 16000, 900, 2100, 2100, 2260, 1180, 1260, 0.69, 0.73, 8, 15, "llm;agent;rag"),
    ("ray-project/ray", "Ray", "AI 与 Python 工作负载分布式计算框架", "Python", "Apache-2.0", 39000, 6800, 520, 2400, 1200, 1700, 520, 760, 0.72, 0.69, 7, 12, "distributed;mlops;scaling"),
    ("jupyter/notebook", "Notebook", "交互式计算笔记本", "Python", "BSD-3-Clause", 11500, 4300, 390, 2300, 620, 260, 180, 120, 0.70, 0.63, 6, 10, "notebook;education;interactive"),
    ("plotly/plotly.py", "Plotly.py", "Python 交互式可视化图库", "Python", "MIT", 16800, 2500, 260, 820, 230, 310, 140, 150, 0.76, 0.68, 6, 9, "visualization;plotly;dashboard"),
    ("streamlit/streamlit", "Streamlit", "数据应用快速开发框架", "Python", "Apache-2.0", 36000, 3200, 390, 980, 520, 820, 360, 410, 0.73, 0.71, 7, 11, "data-app;dashboard;python"),
    ("fastapi/fastapi", "FastAPI", "现代 Python Web API 框架", "Python", "MIT", 82000, 7200, 650, 570, 720, 760, 310, 330, 0.84, 0.76, 8, 13, "api;web;async"),
    ("mlflow/mlflow", "MLflow", "机器学习实验与模型生命周期平台", "Python", "Apache-2.0", 21000, 4300, 330, 1800, 780, 980, 390, 460, 0.71, 0.67, 6, 10, "mlops;experiment;model-registry"),
    ("apache/spark", "Spark", "大规模数据处理计算引擎", "Scala", "Apache-2.0", 40000, 28500, 1800, 5200, 2300, 690, 360, 310, 0.68, 0.61, 10, 16, "big-data;distributed;sql"),
    ("microsoft/LightGBM", "LightGBM", "高性能梯度提升树算法库", "C++", "MIT", 17000, 3900, 360, 620, 320, 120, 90, 70, 0.62, 0.52, 5, 8, "gbdt;machine-learning;ranking"),
    ("xgboost/xgboost", "XGBoost", "可扩展梯度提升算法库", "C++", "Apache-2.0", 26000, 8800, 710, 1100, 610, 210, 130, 120, 0.70, 0.60, 6, 9, "gbdt;boosting;machine-learning"),
    ("facebookresearch/faiss", "FAISS", "高维向量相似搜索库", "C++", "MIT", 34000, 3600, 520, 470, 350, 170, 95, 80, 0.58, 0.48, 5, 7, "vector-search;ann;similarity"),
    ("openai/openai-python", "openai-python", "OpenAI API Python SDK", "Python", "Apache-2.0", 26000, 3600, 240, 420, 260, 900, 280, 360, 0.77, 0.80, 7, 12, "sdk;api;llm"),
    ("elastic/elasticsearch", "Elasticsearch", "分布式搜索与分析引擎", "Java", "Elastic-2.0", 72000, 24500, 3000, 4100, 1900, 540, 330, 280, 0.64, 0.57, 9, 14, "search;analytics;distributed"),
]

PLACES = [
    ("United States", "San Francisco", 37.7749, -122.4194),
    ("United States", "New York", 40.7128, -74.0060),
    ("China", "Beijing", 39.9042, 116.4074),
    ("China", "Shanghai", 31.2304, 121.4737),
    ("United Kingdom", "London", 51.5072, -0.1276),
    ("Germany", "Berlin", 52.5200, 13.4050),
    ("France", "Paris", 48.8566, 2.3522),
    ("India", "Bangalore", 12.9716, 77.5946),
    ("Japan", "Tokyo", 35.6762, 139.6503),
    ("Canada", "Toronto", 43.6532, -79.3832),
    ("Netherlands", "Amsterdam", 52.3676, 4.9041),
    ("Australia", "Sydney", -33.8688, 151.2093),
]


def iso_days_ago(days: int) -> str:
    return (NOW - timedelta(days=days)).date().isoformat()


def build_repos() -> pd.DataFrame:
    rows = []
    for i, item in enumerate(PROJECTS):
        repo, name, desc, language, license_name, stars, forks, watchers, open_issues, contributors, commits, issues, prs, issue_rate, pr_rate, country_count, city_count, topics = item
        rows.append(
            {
                "repo": repo,
                "owner": repo.split("/")[0],
                "name": name,
                "description": desc,
                "stars": stars,
                "forks": forks,
                "watchers": watchers,
                "open_issues": open_issues,
                "language": language,
                "license": license_name,
                "created_at": iso_days_ago(365 * (20 - min(i, 17))),
                "updated_at": iso_days_ago(i % 8),
                "pushed_at": iso_days_ago(i % 5),
                "topics": topics,
                "contributors": contributors,
                "commits_recent": commits,
                "issues_recent": issues,
                "prs_recent": prs,
                "issue_close_rate": issue_rate,
                "pr_merge_rate": pr_rate,
                "country_count": country_count,
                "city_count": city_count,
            }
        )
    return pd.DataFrame(rows)


def build_geo(repos: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    geo_rows, contributor_rows = [], []
    rng = np.random.default_rng(42)
    for _, repo in repos.iterrows():
        weights = rng.dirichlet(np.ones(len(PLACES)) * 1.6)
        for place_index, (country, city, lat, lon) in enumerate(PLACES):
            count = max(1, int(repo["contributors"] * weights[place_index] / 18))
            for j in range(min(count, 18)):
                contributions = int(rng.integers(3, 180))
                row = {
                    "repo": repo["repo"],
                    "login": f"{repo['name'].lower().replace('.', '').replace('-', '')}_{place_index}_{j}",
                    "country": country,
                    "city": city,
                    "lat": lat + float(rng.normal(0, 0.18)),
                    "lon": lon + float(rng.normal(0, 0.18)),
                    "contributions": contributions,
                }
                geo_rows.append(row)
                contributor_rows.append({**row, "role": "contributor"})
    return pd.DataFrame(contributor_rows), pd.DataFrame(geo_rows)


def build_issues_pulls(repos: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    issue_types = ["Bug", "Feature Request", "Documentation", "Installation", "Performance", "Compatibility", "Question"]
    issue_rows, pull_rows = [], []
    for repo_idx, repo in repos.iterrows():
        for i in range(18):
            closed = i / 18 < repo["issue_close_rate"]
            created_days = 7 + i * 3 + repo_idx
            issue_rows.append(
                {
                    "repo": repo["repo"],
                    "issue_id": repo_idx * 1000 + i,
                    "title": f"{repo['name']} {issue_types[i % len(issue_types)]} 示例问题 {i + 1}",
                    "state": "closed" if closed else "open",
                    "created_at": iso_days_ago(created_days),
                    "closed_at": iso_days_ago(max(created_days - 2, 1)) if closed else "",
                    "issue_type": issue_types[i % len(issue_types)],
                }
            )
        for i in range(14):
            merged = i / 14 < repo["pr_merge_rate"]
            closed = merged or i % 5 != 0
            created_days = 5 + i * 4 + repo_idx
            pull_rows.append(
                {
                    "repo": repo["repo"],
                    "pr_id": repo_idx * 1000 + i,
                    "title": f"{repo['name']} PR 改进 {i + 1}",
                    "state": "closed" if closed else "open",
                    "created_at": iso_days_ago(created_days),
                    "closed_at": iso_days_ago(max(created_days - 1, 1)) if closed else "",
                    "merged_at": iso_days_ago(max(created_days - 1, 1)) if merged else "",
                }
            )
    return pd.DataFrame(issue_rows), pd.DataFrame(pull_rows)


def build_text_results(repos: pd.DataFrame) -> pd.DataFrame:
    topics = ["深度学习框架", "数据科学工具", "大模型应用", "分布式计算", "可视化与应用", "搜索与向量检索"]
    rows = []
    for i, repo in repos.iterrows():
        rows.append(
            {
                "repo": repo["repo"],
                "text_cluster": i % len(topics),
                "text_x": round(np.cos(i / 2) * (1 + i % 4 / 5), 4),
                "text_y": round(np.sin(i / 2) * (1 + i % 5 / 6), 4),
                "main_topic": topics[i % len(topics)],
                "readme_keywords": repo["topics"],
                "commit_type": ["fix", "feat", "docs", "refactor", "test", "perf", "chore"][i % 7],
            }
        )
    return pd.DataFrame(rows)


def build_star_history(scores: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for i, row in scores.iterrows():
        growth_30m = (i * 7) % 19
        growth_24h = 20 + (i * 17) % 180
        for label, minutes, stars in [
            ("24h", 24 * 60, max(0, int(row["stars"]) - growth_24h)),
            ("30m", 30, max(0, int(row["stars"]) - growth_30m)),
            ("now", 0, int(row["stars"])),
        ]:
            rows.append(
                {
                    "repo": row["repo"],
                    "stars": stars,
                    "forks": int(row["forks"]),
                    "open_issues": int(row["open_issues"]),
                    "collected_at": (NOW - timedelta(minutes=minutes)).isoformat(),
                    "snapshot_type": label,
                }
            )
    return pd.DataFrame(rows)


def add_initial_scores(repos: pd.DataFrame, geo: pd.DataFrame) -> pd.DataFrame:
    scores = repos.copy()
    country_stats = geo.groupby("repo").agg(country_count=("country", "nunique"), city_count=("city", "nunique")).reset_index()
    top = geo.groupby(["repo", "country"]).size().reset_index(name="count")
    total = geo.groupby("repo").size().reset_index(name="total")
    top = top.sort_values(["repo", "count"], ascending=[True, False]).groupby("repo").first().reset_index().merge(total, on="repo")
    top["top_country_ratio"] = top["count"] / top["total"]
    scores = scores.drop(columns=["country_count", "city_count"]).merge(country_stats, on="repo", how="left").merge(top[["repo", "top_country_ratio"]], on="repo", how="left")

    def minmax(series: pd.Series) -> pd.Series:
        low, high = series.min(), series.max()
        if high == low:
            return pd.Series([0.5] * len(series), index=series.index)
        return (series - low) / (high - low)

    scores["popularity_score"] = 0.5 * minmax(np.log1p(scores["stars"])) + 0.3 * minmax(np.log1p(scores["forks"])) + 0.2 * minmax(np.log1p(scores["watchers"]))
    scores["activity_score"] = 0.4 * minmax(scores["commits_recent"]) + 0.3 * minmax(scores["prs_recent"]) + 0.3 * minmax(scores["issues_recent"])
    scores["health_score"] = 0.25 * scores["issue_close_rate"] + 0.25 * scores["pr_merge_rate"] + 0.25 * minmax(scores["contributors"]) + 0.25 * scores["activity_score"]
    scores["globalization_score"] = 0.4 * minmax(scores["country_count"]) + 0.3 * minmax(scores["city_count"]) + 0.3 * (1 - scores["top_country_ratio"])
    return scores


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    repos = build_repos()
    contributors, geo = build_geo(repos)
    issues, pulls = build_issues_pulls(repos)
    text = build_text_results(repos)
    scores = add_initial_scores(repos, geo)
    star_history = build_star_history(scores)
    scores.to_csv(OUT_DIR / "repos.csv", index=False)
    scores.to_csv(OUT_DIR / "scores.csv", index=False)
    contributors.to_csv(OUT_DIR / "contributors.csv", index=False)
    geo.to_csv(OUT_DIR / "geo_contributors.csv", index=False)
    issues.to_csv(OUT_DIR / "issues.csv", index=False)
    pulls.to_csv(OUT_DIR / "pulls.csv", index=False)
    text.to_csv(OUT_DIR / "text_results.csv", index=False)
    star_history.to_csv(OUT_DIR / "star_history.csv", index=False)
    print(f"已生成 demo 数据到 {OUT_DIR.resolve()}")


if __name__ == "__main__":
    main()
