from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


DATA_DIR = Path("data/processed")


def load_repo_baseline() -> dict[str, int]:
    scores_path = DATA_DIR / "scores.csv"
    if not scores_path.exists():
        return {}
    try:
        scores = pd.read_csv(scores_path, usecols=["repo", "stars"])
    except Exception:
        return {}
    if scores.empty:
        return {}
    scores["repo"] = scores["repo"].astype(str)
    scores["stars"] = pd.to_numeric(scores["stars"], errors="coerce").fillna(0).astype(int)
    return dict(zip(scores["repo"], scores["stars"]))


def nearest_previous(group: pd.DataFrame, target_time: pd.Timestamp) -> pd.Series | None:
    previous = group[group["collected_at"] <= target_time]
    if previous.empty:
        return None
    return previous.iloc[-1]


def build_growth() -> pd.DataFrame:
    history_path = DATA_DIR / "star_history.csv"
    if not history_path.exists():
        return pd.DataFrame(columns=["repo", "stars_latest", "growth_30m", "growth_24h", "snapshot_count", "note", "collected_at"])
    history = pd.read_csv(history_path)
    if history.empty:
        return pd.DataFrame(columns=["repo", "stars_latest", "growth_30m", "growth_24h", "snapshot_count", "note", "collected_at"])
    history["collected_at"] = pd.to_datetime(history["collected_at"], errors="coerce", utc=True)
    history["stars"] = pd.to_numeric(history["stars"], errors="coerce").fillna(0).astype(int)
    repo_baseline = load_repo_baseline()
    if repo_baseline:
        history = history[history["repo"].astype(str).isin(repo_baseline.keys())].copy()
        history["baseline_stars"] = history["repo"].map(repo_baseline).fillna(0).astype(int)
        max_reasonable = (history["baseline_stars"] * 1.25 + 1000).astype(int)
        history = history[(history["baseline_stars"] <= 0) | (history["stars"] <= max_reasonable)].copy()
    history = history.dropna(subset=["collected_at"]).sort_values(["repo", "collected_at"])
    if history.empty:
        return pd.DataFrame(columns=["repo", "stars_latest", "growth_30m", "growth_24h", "snapshot_count", "note", "collected_at"])
    rows = []
    for repo, group in history.groupby("repo"):
        latest = group.iloc[-1]
        ref_30m = nearest_previous(group, latest["collected_at"] - pd.Timedelta(minutes=30))
        ref_24h = nearest_previous(group, latest["collected_at"] - pd.Timedelta(hours=24))
        note_parts = []
        if len(group) < 2:
            note_parts.append("只有一次采集快照，无法计算真实增长")
        else:
            if ref_30m is None:
                note_parts.append("缺少 30 分钟前快照")
            if ref_24h is None:
                note_parts.append("缺少 24 小时前快照")
        if not note_parts:
            note_parts.append("已按历史快照计算")
        rows.append(
            {
                "repo": repo,
                "stars_latest": int(latest["stars"]),
                "stars_30m_ago": int(ref_30m["stars"]) if ref_30m is not None else int(group.iloc[0]["stars"]),
                "stars_24h_ago": int(ref_24h["stars"]) if ref_24h is not None else int(group.iloc[0]["stars"]),
                "growth_30m": int(latest["stars"] - (ref_30m["stars"] if ref_30m is not None else group.iloc[0]["stars"])),
                "growth_24h": int(latest["stars"] - (ref_24h["stars"] if ref_24h is not None else group.iloc[0]["stars"])),
                "window_30m_available": ref_30m is not None,
                "window_24h_available": ref_24h is not None,
                "snapshot_count": len(group),
                "note": "；".join(note_parts),
                "collected_at": latest["collected_at"].isoformat(),
            }
        )
    return pd.DataFrame(rows).sort_values(["growth_30m", "growth_24h", "stars_latest"], ascending=False)


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    growth = build_growth()
    growth.to_csv(DATA_DIR / "star_growth.csv", index=False)
    metadata_path = DATA_DIR / "refresh_metadata.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8")) if metadata_path.exists() else {}
    metadata.update({"star_growth_built_at": datetime.now(timezone.utc).isoformat(), "star_growth_rows": len(growth)})
    metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"已生成 Star 增长排行：{DATA_DIR / 'star_growth.csv'}")


if __name__ == "__main__":
    main()
