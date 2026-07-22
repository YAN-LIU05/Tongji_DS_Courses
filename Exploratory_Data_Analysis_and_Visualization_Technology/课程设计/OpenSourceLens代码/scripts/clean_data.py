from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


DATA_DIR = Path("data/processed")
REQUIRED_REPO_COLUMNS = [
    "repo",
    "owner",
    "name",
    "description",
    "stars",
    "forks",
    "watchers",
    "open_issues",
    "language",
    "license",
    "created_at",
    "updated_at",
    "pushed_at",
    "topics",
    "contributors",
    "commits_recent",
    "issues_recent",
    "prs_recent",
    "issue_close_rate",
    "pr_merge_rate",
    "country_count",
    "city_count",
]


def safe_read(path: Path) -> pd.DataFrame:
    return pd.read_csv(path) if path.exists() else pd.DataFrame()


def normalize_repo_table(df: pd.DataFrame) -> pd.DataFrame:
    for col in REQUIRED_REPO_COLUMNS:
        if col not in df.columns:
            df[col] = "" if col in {"repo", "owner", "name", "description", "language", "license", "created_at", "updated_at", "pushed_at", "topics"} else 0
    numeric_cols = [
        "stars",
        "forks",
        "watchers",
        "open_issues",
        "contributors",
        "commits_recent",
        "issues_recent",
        "prs_recent",
        "issue_close_rate",
        "pr_merge_rate",
        "country_count",
        "city_count",
    ]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    df["repo"] = df["repo"].astype(str).str.strip()
    df["owner"] = df["owner"].where(df["owner"].astype(str).str.len() > 0, df["repo"].str.split("/").str[0])
    df["name"] = df["name"].where(df["name"].astype(str).str.len() > 0, df["repo"].str.split("/").str[-1])
    df["language"] = df["language"].fillna("Unknown").replace("", "Unknown")
    return df.drop_duplicates("repo").sort_values("stars", ascending=False)


def normalize_dates(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    for col in columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce", utc=True).dt.strftime("%Y-%m-%d")
            df[col] = df[col].fillna("")
    return df


def main() -> None:
    repos = safe_read(DATA_DIR / "repos.csv")
    if repos.empty:
        raise FileNotFoundError("缺少 data/processed/repos.csv，请先运行 scripts/collect_github_data.py 或 scripts/generate_demo_data.py")
    repos = normalize_repo_table(repos)
    repos = normalize_dates(repos, ["created_at", "updated_at", "pushed_at"])
    repos.to_csv(DATA_DIR / "repos.csv", index=False)
    repos.to_csv(DATA_DIR / "scores.csv", index=False)

    for file_name, date_cols in {
        "issues.csv": ["created_at", "closed_at"],
        "pulls.csv": ["created_at", "closed_at", "merged_at"],
    }.items():
        path = DATA_DIR / file_name
        df = safe_read(path)
        if not df.empty:
            normalize_dates(df, date_cols).to_csv(path, index=False)

    metadata_path = DATA_DIR / "refresh_metadata.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8")) if metadata_path.exists() else {}
    metadata.update({"cleaned_at": datetime.now(timezone.utc).isoformat(), "repo_count": len(repos)})
    metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"已清洗数据：{DATA_DIR}")


if __name__ == "__main__":
    main()
