from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd


DATA_DIR = Path("data/processed")


def minmax(series: pd.Series) -> pd.Series:
    series = pd.to_numeric(series, errors="coerce").fillna(0)
    low, high = series.min(), series.max()
    if high == low:
        return pd.Series([0.5] * len(series), index=series.index)
    return (series - low) / (high - low)


def read_required(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"缺少输入文件：{path}，请先运行 scripts/generate_demo_data.py")
    return pd.read_csv(path)


def add_first_year_star_features(scores: pd.DataFrame) -> pd.DataFrame:
    if "created_at" not in scores.columns or "stars" not in scores.columns:
        scores["stars_first_year_estimate"] = 0
        scores["repo_age_days"] = 0
        scores["first_year_window_observed"] = False
        return scores

    created = pd.to_datetime(scores["created_at"], errors="coerce", utc=True)
    if "collected_at" in scores.columns:
        collected = pd.to_datetime(scores["collected_at"], errors="coerce", utc=True)
    else:
        collected = pd.Series(pd.NaT, index=scores.index, dtype="datetime64[ns, UTC]")
    collected = collected.fillna(pd.Timestamp.now(tz=timezone.utc))
    age_days = (collected - created).dt.total_seconds().div(86400).clip(lower=1).fillna(1)
    stars = pd.to_numeric(scores["stars"], errors="coerce").fillna(0)
    first_year_estimate = np.where(age_days >= 365, stars * 365 / age_days, stars)
    scores["repo_age_days"] = age_days.round().astype(int)
    scores["stars_first_year_estimate"] = np.minimum(first_year_estimate, stars).round().astype(int)
    scores["first_year_window_observed"] = age_days >= 365
    return scores


def build_scores() -> pd.DataFrame:
    repos = read_required(DATA_DIR / "repos.csv")
    geo = pd.read_csv(DATA_DIR / "geo_contributors.csv") if (DATA_DIR / "geo_contributors.csv").exists() else pd.DataFrame()

    scores = repos.copy()
    if not geo.empty:
        country_stats = geo.groupby("repo").agg(country_count=("country", "nunique"), city_count=("city", "nunique")).reset_index()
        top_ratio = (
            geo.groupby(["repo", "country"]).size().reset_index(name="count").sort_values(["repo", "count"], ascending=[True, False]).groupby("repo").first().reset_index()
        )
        total = geo.groupby("repo").size().reset_index(name="total")
        top_ratio = top_ratio.merge(total, on="repo")
        top_ratio["top_country_ratio"] = top_ratio["count"] / top_ratio["total"]
        scores = scores.drop(columns=[c for c in ["country_count", "city_count", "top_country_ratio"] if c in scores.columns])
        scores = scores.merge(country_stats, on="repo", how="left").merge(top_ratio[["repo", "top_country_ratio"]], on="repo", how="left")
    else:
        scores["top_country_ratio"] = 0.55

    for col in ["country_count", "city_count", "top_country_ratio"]:
        scores[col] = pd.to_numeric(scores.get(col, 0), errors="coerce").fillna(0)

    scores["popularity_score"] = (
        0.5 * minmax(np.log1p(scores["stars"]))
        + 0.3 * minmax(np.log1p(scores["forks"]))
        + 0.2 * minmax(np.log1p(scores["watchers"]))
    ).clip(0, 1)
    scores["activity_score"] = (
        0.4 * minmax(scores["commits_recent"])
        + 0.3 * minmax(scores["prs_recent"])
        + 0.3 * minmax(scores["issues_recent"])
    ).clip(0, 1)
    scores["health_score"] = (
        0.25 * pd.to_numeric(scores["issue_close_rate"], errors="coerce").fillna(0)
        + 0.25 * pd.to_numeric(scores["pr_merge_rate"], errors="coerce").fillna(0)
        + 0.25 * minmax(scores["contributors"])
        + 0.25 * scores["activity_score"]
    ).clip(0, 1)
    scores["globalization_score"] = (
        0.4 * minmax(scores["country_count"])
        + 0.3 * minmax(scores["city_count"])
        + 0.3 * (1 - scores["top_country_ratio"].clip(0, 1))
    ).clip(0, 1)
    scores = add_first_year_star_features(scores)
    return scores


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    scores = build_scores()
    scores.to_csv(DATA_DIR / "scores.csv", index=False)
    scores.to_csv(DATA_DIR / "repos.csv", index=False)
    metadata_path = DATA_DIR / "refresh_metadata.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8")) if metadata_path.exists() else {}
    metadata.update({"featured_at": datetime.now(timezone.utc).isoformat(), "repo_count": len(scores)})
    metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"已生成特征评分：{DATA_DIR / 'scores.csv'}")


if __name__ == "__main__":
    main()
