from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


DATA_DIR = Path("data/processed")


def safe_read_csv(path: str | Path) -> pd.DataFrame:
    csv_path = Path(path)
    if not csv_path.exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(csv_path)
    except Exception:
        return pd.DataFrame()


def load_repos() -> pd.DataFrame:
    return safe_read_csv(DATA_DIR / "repos.csv")


def load_scores() -> pd.DataFrame:
    return safe_read_csv(DATA_DIR / "scores.csv")


def load_contributors() -> pd.DataFrame:
    return safe_read_csv(DATA_DIR / "contributors.csv")


def load_geo_contributors() -> pd.DataFrame:
    return safe_read_csv(DATA_DIR / "geo_contributors.csv")


def load_issues() -> pd.DataFrame:
    return safe_read_csv(DATA_DIR / "issues.csv")


def load_pulls() -> pd.DataFrame:
    return safe_read_csv(DATA_DIR / "pulls.csv")


def load_ml_results() -> pd.DataFrame:
    return safe_read_csv(DATA_DIR / "ml_results.csv")


def load_text_results() -> pd.DataFrame:
    return safe_read_csv(DATA_DIR / "text_results.csv")


def load_text_similarity() -> pd.DataFrame:
    return safe_read_csv(DATA_DIR / "text_similarity.csv")


def load_star_growth() -> pd.DataFrame:
    return safe_read_csv(DATA_DIR / "star_growth.csv")


def load_star_history() -> pd.DataFrame:
    return safe_read_csv(DATA_DIR / "star_history.csv")


def load_model_metrics() -> pd.DataFrame:
    return safe_read_csv(DATA_DIR / "model_metrics.csv")


def load_cluster_profiles() -> pd.DataFrame:
    return safe_read_csv(DATA_DIR / "cluster_profiles.csv")


def dataframe_records(df: pd.DataFrame) -> list[dict]:
    if df.empty:
        return []
    return df.fillna("").to_dict(orient="records")


def load_refresh_metadata() -> dict:
    path = DATA_DIR / "refresh_metadata.json"
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def processed_fingerprint() -> str:
    files = [
        "repos.csv",
        "scores.csv",
        "contributors.csv",
        "geo_contributors.csv",
        "issues.csv",
        "pulls.csv",
        "ml_results.csv",
        "model_metrics.csv",
        "cluster_profiles.csv",
        "text_results.csv",
        "text_similarity.csv",
        "star_growth.csv",
        "star_history.csv",
        "refresh_metadata.json",
    ]
    parts = []
    for name in files:
        path = DATA_DIR / name
        if path.exists():
            stat = path.stat()
            parts.append(f"{name}:{stat.st_mtime_ns}:{stat.st_size}")
    return "|".join(parts)
