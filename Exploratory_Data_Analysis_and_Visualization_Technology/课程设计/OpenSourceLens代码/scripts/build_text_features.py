from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


DATA_DIR = Path("data/processed")


def main() -> None:
    score_path = DATA_DIR / "scores.csv"
    if not score_path.exists():
        raise FileNotFoundError("缺少 data/processed/scores.csv，请先运行 scripts/build_features.py")

    scores = pd.read_csv(score_path)
    corpus_path = DATA_DIR / "text_corpus.csv"
    if corpus_path.exists():
        corpus = pd.read_csv(corpus_path).drop_duplicates("repo")
        merged = scores[["repo", "description", "topics", "language"]].merge(corpus, on="repo", how="left")
        text = merged["source_text"].fillna(merged["description"].fillna("") + " " + merged["topics"].fillna("") + " " + merged["language"].fillna("")).tolist()
    else:
        merged = scores.copy()
        merged["source_text"] = scores["description"].fillna("") + " " + scores["topics"].fillna("") + " " + scores["language"].fillna("")
        text = merged["source_text"].tolist()
    topic_names = ["深度学习框架", "数据科学工具", "大模型应用", "分布式计算", "可视化与应用", "搜索与向量检索"]

    try:
        from sentence_transformers import SentenceTransformer

        embeddings = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2").encode(text, normalize_embeddings=True)
    except Exception:
        embeddings = TfidfVectorizer(max_features=64).fit_transform(text).toarray()

    if embeddings.shape[1] < 2:
        embeddings = np.pad(embeddings, ((0, 0), (0, 2 - embeddings.shape[1])))
    if len(scores) < 2:
        coords = np.zeros((len(scores), 2))
        labels = np.zeros(len(scores), dtype=int)
    else:
        coords = PCA(n_components=2, random_state=42).fit_transform(embeddings)
        labels = KMeans(n_clusters=min(6, len(scores)), n_init=10, random_state=42).fit_predict(embeddings)
    similarity = cosine_similarity(embeddings)
    similarity_rows = []
    repos = scores["repo"].astype(str).tolist()
    for i, repo_a in enumerate(repos):
        for j, repo_b in enumerate(repos):
            similarity_rows.append(
                {
                    "repo_a": repo_a,
                    "repo_b": repo_b,
                    "similarity": round(float(similarity[i, j]), 6),
                }
            )
    rows = []
    for i, row in scores.iterrows():
        rows.append(
            {
                "repo": row["repo"],
                "text_cluster": int(labels[i]),
                "text_x": coords[i, 0],
                "text_y": coords[i, 1],
                "main_topic": topic_names[int(labels[i]) % len(topic_names)],
                "readme_keywords": merged.iloc[i].get("readme_keywords", row.get("topics", "")),
                "commit_type": merged.iloc[i].get("commit_type", ["fix", "feat", "docs", "refactor", "test", "perf", "chore"][i % 7]),
            }
        )
    pd.DataFrame(rows).to_csv(DATA_DIR / "text_results.csv", index=False)
    pd.DataFrame(similarity_rows).to_csv(DATA_DIR / "text_similarity.csv", index=False)
    np.save(DATA_DIR / "text_embeddings.npy", embeddings)
    metadata_path = DATA_DIR / "refresh_metadata.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8")) if metadata_path.exists() else {}
    metadata.update(
        {
            "text_built_at": datetime.now(timezone.utc).isoformat(),
            "text_similarity_file": "data/processed/text_similarity.csv",
            "text_embedding_file": "data/processed/text_embeddings.npy",
            "text_similarity_rows": len(similarity_rows),
        }
    )
    metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"已生成文本语义结果：{DATA_DIR / 'text_results.csv'}")


if __name__ == "__main__":
    main()
