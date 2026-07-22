from __future__ import annotations

import os
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone
from html import unescape
from pathlib import Path
from typing import Any
from urllib.parse import quote

import pandas as pd
import requests
from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data" / "processed"
API = "https://api.github.com"
TRENDING_URL = "https://github.com/trending"
load_dotenv(PROJECT_ROOT / ".env", override=False)

TRENDING_LANGUAGE_SLUGS = {
    "Python": "python",
    "TypeScript": "typescript",
    "JavaScript": "javascript",
    "Rust": "rust",
    "Go": "go",
    "Java": "java",
    "C++": "c++",
    "Jupyter Notebook": "jupyter-notebook",
}

TRENDING_SINCE_VALUES = {
    "今日": "daily",
    "本周": "weekly",
    "本月": "monthly",
    "daily": "daily",
    "weekly": "weekly",
    "monthly": "monthly",
}


def _token() -> str:
    return (os.getenv("GITHUB_TOKEN") or "").strip().strip('"').strip("'")


def _headers(star_timestamps: bool = False) -> dict[str, str]:
    accept = "application/vnd.github.star+json" if star_timestamps else "application/vnd.github+json"
    headers = {
        "Accept": accept,
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "OpenSourceLens-Realtime-Stars",
    }
    token = _token()
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _get_json(url: str, params: dict[str, Any] | None = None, star_timestamps: bool = False) -> tuple[Any, requests.Response]:
    response = requests.get(url, headers=_headers(star_timestamps), params=params, timeout=10)
    if response.status_code == 403 and response.headers.get("X-RateLimit-Remaining") == "0":
        reset = response.headers.get("X-RateLimit-Reset")
        raise RuntimeError(f"GitHub API 速率限制已用尽，请稍后重试；建议配置 GITHUB_TOKEN。Reset={reset}")
    response.raise_for_status()
    return response.json(), response


def _get_html(url: str, params: dict[str, Any] | None = None) -> str:
    response = requests.get(
        url,
        headers={
            "Accept": "text/html,application/xhtml+xml",
            "User-Agent": "OpenSourceLens-Trending-Collector",
        },
        params=params,
        timeout=10,
    )
    response.raise_for_status()
    return response.text


def _clean_html_text(value: str) -> str:
    text = re.sub(r"<[^>]+>", " ", value or "")
    return re.sub(r"\s+", " ", unescape(text)).strip()


def _parse_count(value: str) -> int:
    text = _clean_html_text(value).replace(",", "").strip().lower()
    match = re.search(r"([0-9]+(?:\.[0-9]+)?)([km]?)", text)
    if not match:
        return 0
    number = float(match.group(1))
    suffix = match.group(2)
    if suffix == "k":
        number *= 1000
    elif suffix == "m":
        number *= 1000000
    return int(number)


def fetch_trending_projects(language: str, since_label: str, limit: int = 30) -> tuple[list[dict], str]:
    slug = TRENDING_LANGUAGE_SLUGS.get(language, "")
    since = TRENDING_SINCE_VALUES.get(since_label, "daily")
    url = f"{TRENDING_URL}/{quote(slug, safe='')}" if slug else TRENDING_URL
    source = f"GitHub Trending {since}"
    if language and language != "全部语言":
        source = f"{source} / {language}"
    html = _get_html(url, {"since": since})
    articles = re.findall(r"<article\b.*?</article>", html, flags=re.IGNORECASE | re.DOTALL)
    rows: list[dict] = []
    seen: set[str] = set()
    collected_at = datetime.now(timezone.utc).isoformat()

    for article in articles:
        match = re.search(r"<h2\b.*?href=\"/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)\"", article, flags=re.IGNORECASE | re.DOTALL)
        if not match:
            match = re.search(r'href="/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)"', article)
        if not match:
            continue
        owner, name = match.group(1), match.group(2)
        repo = f"{owner}/{name}"
        if repo not in seen:
            desc_match = re.search(r"<p\b[^>]*>(.*?)</p>", article, flags=re.IGNORECASE | re.DOTALL)
            lang_match = re.search(r'itemprop="programmingLanguage"[^>]*>(.*?)</span>', article, flags=re.IGNORECASE | re.DOTALL)
            stars_match = re.search(rf'href="/{re.escape(owner)}/{re.escape(name)}/stargazers"[^>]*>(.*?)</a>', article, flags=re.IGNORECASE | re.DOTALL)
            forks_match = re.search(rf'href="/{re.escape(owner)}/{re.escape(name)}/forks"[^>]*>(.*?)</a>', article, flags=re.IGNORECASE | re.DOTALL)
            article_text = _clean_html_text(article)
            period_match = re.search(r"([0-9][0-9,]*)\s+stars?\s+(today|this week|this month)", article_text, flags=re.IGNORECASE)
            rows.append(
                {
                    "rank": len(rows) + 1,
                    "repo": repo,
                    "owner": owner,
                    "name": name,
                    "language": _clean_html_text(lang_match.group(1)) if lang_match else "Unknown",
                    "stars": _parse_count(stars_match.group(1)) if stars_match else 0,
                    "forks": _parse_count(forks_match.group(1)) if forks_match else 0,
                    "period_stars": _parse_count(period_match.group(1)) if period_match else 0,
                    "period_label": since_label,
                    "description": _clean_html_text(desc_match.group(1)) if desc_match else "",
                    "url": f"https://github.com/{repo}",
                    "source": source,
                    "collected_at": collected_at,
                }
            )
            seen.add(repo)
        if len(rows) >= limit:
            break

    if not rows:
        for owner, name in re.findall(r'href="/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)"', html):
            repo = f"{owner}/{name}"
            if repo not in seen:
                rows.append(
                    {
                        "rank": len(rows) + 1,
                        "repo": repo,
                        "owner": owner,
                        "name": name,
                        "language": "Unknown",
                        "stars": 0,
                        "forks": 0,
                        "period_stars": 0,
                        "period_label": since_label,
                        "description": "",
                        "url": f"https://github.com/{repo}",
                        "source": source,
                        "collected_at": collected_at,
                    }
                )
                seen.add(repo)
            if len(rows) >= limit:
                break

    return rows[:limit], source


def discover_trending_repos(language: str, since_label: str, limit: int = 30) -> tuple[list[str], str]:
    rows, source = fetch_trending_projects(language, since_label, limit)
    return [str(row.get("repo", "")) for row in rows if row.get("repo")], source


def _normalize_star_rank_query(query: str, language: str) -> str:
    search_query = (query or "").strip() or "stars:>1000"
    lower = search_query.lower()
    if "fork:" not in lower:
        search_query = f"{search_query} fork:false"
    if "archived:" not in lower:
        search_query = f"{search_query} archived:false"
    if language and language != "全部语言" and "language:" not in lower:
        search_query = f'{search_query} language:"{language}"'
    return search_query


def fetch_star_rank_projects(query: str, language: str, limit: int = 30) -> tuple[list[dict], str]:
    search_query = _normalize_star_rank_query(query, language)
    collected_at = datetime.now(timezone.utc).isoformat()
    data, _ = _get_json(
        f"{API}/search/repositories",
        {
            "q": search_query,
            "sort": "stars",
            "order": "desc",
            "per_page": max(1, min(100, limit)),
        },
    )
    items = data.get("items", []) if isinstance(data, dict) else []
    rows: list[dict] = []
    seen: set[str] = set()
    for item in items:
        if not isinstance(item, dict):
            continue
        repo = str(item.get("full_name", ""))
        if not repo or repo in seen:
            continue
        owner = item.get("owner") or {}
        rows.append(
            {
                "rank": len(rows) + 1,
                "repo": repo,
                "owner": owner.get("login", repo.split("/")[0]) if isinstance(owner, dict) else repo.split("/")[0],
                "name": item.get("name", repo.split("/")[-1]),
                "language": item.get("language") or "Unknown",
                "stars": int(item.get("stargazers_count", 0) or 0),
                "forks": int(item.get("forks_count", 0) or 0),
                "open_issues": int(item.get("open_issues_count", 0) or 0),
                "description": item.get("description") or "",
                "url": item.get("html_url") or f"https://github.com/{repo}",
                "updated_at": item.get("updated_at", ""),
                "pushed_at": item.get("pushed_at", ""),
                "source": "GitHub Search Stars",
                "collected_at": collected_at,
            }
        )
        seen.add(repo)
        if len(rows) >= limit:
            break
    return rows, search_query


def _last_page(link_header: str | None) -> int:
    if not link_header:
        return 1
    match = re.search(r"[?&]page=(\d+)>;\s*rel=\"last\"", link_header)
    return int(match.group(1)) if match else 1


def _parse_time(value: str) -> datetime | None:
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)
    except Exception:
        return None


def _count_recent_star_events(repo: str, now: datetime, max_pages: int = 6) -> tuple[int, int, str]:
    cutoff_30m = now - timedelta(minutes=30)
    cutoff_24h = now - timedelta(hours=24)
    growth_30m = 0
    growth_24h = 0
    note = ""
    reached_older_than_24h = False

    first_page, first_response = _get_json(
        f"{API}/repos/{repo}/stargazers",
        {"per_page": 100, "page": 1},
        star_timestamps=True,
    )
    last_page = _last_page(first_response.headers.get("Link"))
    pages = range(last_page, max(0, last_page - max_pages), -1)

    for page in pages:
        data = first_page if page == 1 else _get_json(
            f"{API}/repos/{repo}/stargazers",
            {"per_page": 100, "page": page},
            star_timestamps=True,
        )[0]
        if not data:
            continue
        seen_times: list[datetime] = []
        for item in data:
            starred_at = _parse_time(str(item.get("starred_at", ""))) if isinstance(item, dict) else None
            if starred_at is None:
                note = "GitHub 未返回 starred_at，无法统计实时窗口。"
                continue
            seen_times.append(starred_at)
            if starred_at >= cutoff_24h:
                growth_24h += 1
            if starred_at >= cutoff_30m:
                growth_30m += 1
        if seen_times and min(seen_times) < cutoff_24h:
            reached_older_than_24h = True
            break
    if last_page > max_pages and not note and not reached_older_than_24h:
        note = f"最多回看最近 {max_pages * 100} 条 Star 事件。"
    return growth_30m, growth_24h, note


def fetch_one_realtime_star_growth(repo: str, now: datetime, source_label: str = "github_realtime") -> dict:
    repo_data, _ = _get_json(f"{API}/repos/{repo}")
    stars_latest = int(repo_data.get("stargazers_count", 0) or 0)
    growth_30m, growth_24h, note = _count_recent_star_events(repo, now)
    return {
        "repo": repo,
        "stars_latest": stars_latest,
        "growth_30m": growth_30m,
        "growth_24h": growth_24h,
        "window_30m_available": True,
        "window_24h_available": True,
        "collected_at": now.isoformat(),
        "source": source_label,
        "note": note,
    }


def _build_status(rows: list[dict], errors: list[str], completed: int, total: int, done: bool = False) -> str:
    if done:
        status = f"已实时查询 {len(rows)} 个项目。"
    else:
        status = f"正在实时查询 GitHub Stars 增长：已完成 {completed}/{total}。"
    if errors:
        status += f" 失败 {len(errors)} 个：{'；'.join(errors[:3])}"
    if not _token():
        status += " 当前未配置 GITHUB_TOKEN，GitHub 匿名接口很容易限流。"
    return status


def iter_realtime_star_growth(repos: list[str], limit: int = 30, source_label: str = "github_realtime"):
    now = datetime.now(timezone.utc)
    rows: list[dict] = []
    errors: list[str] = []
    selected_repos = [repo for repo in repos if repo][:limit]
    total = len(selected_repos)
    if total == 0:
        yield {"rows": rows, "errors": errors, "completed": 0, "total": 0, "status": "没有可查询的项目。", "done": True}
        return

    workers = min(8, max(1, len(selected_repos)))
    yield {
        "rows": rows,
        "errors": errors,
        "completed": 0,
        "total": total,
        "status": f"正在实时查询 GitHub Stars 增长：已完成 0/{total}。",
        "done": False,
    }
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(fetch_one_realtime_star_growth, repo, now, source_label): repo for repo in selected_repos}
        completed = 0
        for future in as_completed(futures):
            repo = futures[future]
            completed += 1
            try:
                rows.append(future.result())
            except Exception as exc:
                errors.append(f"{repo}: {exc}")
            sorted_rows = sorted(rows, key=lambda row: (row["growth_30m"], row["growth_24h"], row["stars_latest"]), reverse=True)
            yield {
                "rows": sorted_rows,
                "errors": errors.copy(),
                "completed": completed,
                "total": total,
                "status": _build_status(sorted_rows, errors, completed, total, done=completed == total),
                "done": completed == total,
            }


def fetch_realtime_star_growth(repos: list[str], limit: int = 30) -> tuple[list[dict], str]:
    last_update = {"rows": [], "status": "没有可查询的项目。"}
    for update in iter_realtime_star_growth(repos, limit):
        last_update = update
    rows = last_update.get("rows", [])
    status = str(last_update.get("status", "没有可查询的项目。"))
    return rows, status


def persist_realtime_star_growth(rows: list[dict]) -> None:
    if not rows:
        return
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    growth_path = DATA_DIR / "star_growth.csv"
    history_path = DATA_DIR / "star_history.csv"
    pd.DataFrame(rows).to_csv(growth_path, index=False)

    snapshot = pd.DataFrame(
        [{"repo": row["repo"], "stars": row["stars_latest"], "collected_at": row["collected_at"]} for row in rows]
    )
    if history_path.exists():
        history = pd.read_csv(history_path)
        history = pd.concat([history, snapshot], ignore_index=True)
    else:
        history = snapshot
    history = history.drop_duplicates(subset=["repo", "collected_at"], keep="last")
    history.to_csv(history_path, index=False)
