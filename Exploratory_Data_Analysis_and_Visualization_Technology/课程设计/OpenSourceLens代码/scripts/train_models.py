from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import joblib
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.ensemble import IsolationForest
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler


DATA_DIR = Path("data/processed")
MODEL_DIR = Path("models")
FEATURES = [
    "stars",
    "forks",
    "open_issues",
    "contributors",
    "commits_recent",
    "issues_recent",
    "prs_recent",
    "issue_close_rate",
    "pr_merge_rate",
    "popularity_score",
    "activity_score",
    "health_score",
    "globalization_score",
]


def anomaly_reason(row: pd.Series) -> str:
    reasons = []
    if row["popularity_score"] >= 0.72 and row["activity_score"] <= 0.42:
        reasons.append("高热度低活跃")
    if row["issues_recent"] >= 500 and row["issue_close_rate"] <= 0.72:
        reasons.append("维护压力型")
    if row["prs_recent"] >= 300 and row["pr_merge_rate"] <= 0.66:
        reasons.append("PR 接纳不足")
    if row["globalization_score"] <= 0.38:
        reasons.append("国际化不足")
    if row["activity_score"] >= 0.75 and row["popularity_score"] <= 0.70:
        reasons.append("潜力成长型")
    return "、".join(reasons) if reasons else "正常"


def cluster_label(row: pd.Series) -> str:
    popularity = float(row.get("popularity_score", 0) or 0)
    activity = float(row.get("activity_score", 0) or 0)
    health = float(row.get("health_score", 0) or 0)
    globalization = float(row.get("globalization_score", 0) or 0)
    if popularity >= 0.65 and activity >= 0.55 and health >= 0.55:
        return "头部活跃型"
    if popularity >= 0.65 and activity < 0.45:
        return "高热度维护压力型"
    if activity >= 0.55 and popularity < 0.55:
        return "潜力成长型"
    if health < 0.35:
        return "健康风险型"
    if globalization >= 0.55:
        return "国际化社区型"
    return "均衡观察型"


def cluster_description(row: pd.Series) -> str:
    label = row.get("cluster_label", "均衡观察型")
    representative = row.get("representative_repo", "代表项目")
    return f"{label}，代表项目为 {representative}；建议结合热度、活跃度、健康度和国际化均值解释该类项目的生态位置。"


def main() -> None:
    score_path = DATA_DIR / "scores.csv"
    if not score_path.exists():
        raise FileNotFoundError("缺少 data/processed/scores.csv，请先运行 scripts/build_features.py")

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(score_path)
    x = df[FEATURES].apply(pd.to_numeric, errors="coerce").fillna(0)

    scaler = StandardScaler()
    x_scaled = scaler.fit_transform(x)
    kmeans = KMeans(n_clusters=min(4, len(df)), n_init=20, random_state=42)
    clusters = kmeans.fit_predict(x_scaled)
    pca = PCA(n_components=2, random_state=42)
    coords = pca.fit_transform(x_scaled)
    iso = IsolationForest(n_estimators=250, contamination=min(0.2, max(0.08, 2 / len(df))), random_state=42)
    anomaly_flags = iso.fit_predict(x_scaled)
    cluster_count = len(set(clusters))
    silhouette = silhouette_score(x_scaled, clusters) if 1 < cluster_count < len(df) else 0.0

    result = df.copy()
    result["cluster"] = clusters
    result["pca_x"] = coords[:, 0]
    result["pca_y"] = coords[:, 1]
    result["anomaly_label"] = ["anomaly" if flag == -1 else "normal" for flag in anomaly_flags]
    result["anomaly_reason"] = [anomaly_reason(row) for _, row in result.iterrows()]
    result.loc[(result["anomaly_label"] == "anomaly") & (result["anomaly_reason"] == "正常"), "anomaly_reason"] = "多维指标偏离常规项目"

    columns = [
        "repo",
        "cluster",
        "pca_x",
        "pca_y",
        "anomaly_label",
        "anomaly_reason",
        "stars",
        "forks",
        "contributors",
        "commits_recent",
        "issues_recent",
        "prs_recent",
        "popularity_score",
        "activity_score",
        "health_score",
        "globalization_score",
    ]
    result[columns].to_csv(DATA_DIR / "ml_results.csv", index=False)

    metrics = pd.DataFrame(
        [
            {"metric": "样本项目数", "value": len(df), "description": "参与本次离线建模的仓库数量。"},
            {"metric": "输入特征数", "value": len(FEATURES), "description": "用于标准化、聚类、降维和异常检测的数值特征数量。"},
            {"metric": "K-Means 聚类数", "value": cluster_count, "description": "K-Means 实际使用的聚类数量。"},
            {"metric": "K-Means Inertia", "value": round(float(kmeans.inertia_), 6), "description": "簇内平方和，越低表示簇内更紧凑；需结合样本规模解释。"},
            {"metric": "Silhouette Score", "value": round(float(silhouette), 6), "description": "轮廓系数，越接近 1 表示聚类分离度越好。"},
            {"metric": "PCA 第一主成分解释率", "value": round(float(pca.explained_variance_ratio_[0]), 6), "description": "PCA 1 对标准化特征方差的解释比例。"},
            {"metric": "PCA 第二主成分解释率", "value": round(float(pca.explained_variance_ratio_[1]), 6), "description": "PCA 2 对标准化特征方差的解释比例。"},
            {"metric": "PCA 累计解释率", "value": round(float(pca.explained_variance_ratio_.sum()), 6), "description": "二维 PCA 对原始多维特征的总解释比例。"},
            {"metric": "异常项目数", "value": int((anomaly_flags == -1).sum()), "description": "Isolation Forest 判定为异常的项目数量。"},
            {"metric": "异常项目占比", "value": round(float((anomaly_flags == -1).mean()), 6), "description": "异常项目数占全部项目的比例。"},
        ]
    )
    metrics.to_csv(DATA_DIR / "model_metrics.csv", index=False)

    profile_rows = []
    for cluster, group in result.groupby("cluster"):
        averages = group[
            ["popularity_score", "activity_score", "health_score", "globalization_score", "stars", "forks", "contributors"]
        ].mean(numeric_only=True)
        representative = group.sort_values(["popularity_score", "activity_score", "health_score"], ascending=False).iloc[0]
        row = {
            "cluster": int(cluster),
            "project_count": int(len(group)),
            "representative_repo": representative["repo"],
            "avg_popularity_score": round(float(averages.get("popularity_score", 0)), 6),
            "avg_activity_score": round(float(averages.get("activity_score", 0)), 6),
            "avg_health_score": round(float(averages.get("health_score", 0)), 6),
            "avg_globalization_score": round(float(averages.get("globalization_score", 0)), 6),
            "avg_stars": round(float(averages.get("stars", 0)), 2),
            "avg_forks": round(float(averages.get("forks", 0)), 2),
            "avg_contributors": round(float(averages.get("contributors", 0)), 2),
        }
        row["cluster_label"] = cluster_label(
            pd.Series(
                {
                    "popularity_score": row["avg_popularity_score"],
                    "activity_score": row["avg_activity_score"],
                    "health_score": row["avg_health_score"],
                    "globalization_score": row["avg_globalization_score"],
                }
            )
        )
        row["description"] = cluster_description(pd.Series(row))
        profile_rows.append(row)
    pd.DataFrame(profile_rows).sort_values("cluster").to_csv(DATA_DIR / "cluster_profiles.csv", index=False)

    joblib.dump(scaler, MODEL_DIR / "scaler.pkl")
    joblib.dump(kmeans, MODEL_DIR / "kmeans.pkl")
    joblib.dump(pca, MODEL_DIR / "pca.pkl")
    joblib.dump(iso, MODEL_DIR / "isolation_forest.pkl")
    metadata_path = DATA_DIR / "refresh_metadata.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8")) if metadata_path.exists() else {}
    metadata.update(
        {
            "trained_at": datetime.now(timezone.utc).isoformat(),
            "model_files": ["models/scaler.pkl", "models/kmeans.pkl", "models/pca.pkl", "models/isolation_forest.pkl"],
            "model_metrics_file": "data/processed/model_metrics.csv",
            "cluster_profiles_file": "data/processed/cluster_profiles.csv",
        }
    )
    metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"已生成机器学习结果：{DATA_DIR / 'ml_results.csv'}")


if __name__ == "__main__":
    main()
