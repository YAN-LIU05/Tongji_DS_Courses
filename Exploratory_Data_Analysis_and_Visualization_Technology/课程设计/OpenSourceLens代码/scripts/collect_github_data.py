from __future__ import annotations

import argparse
import base64
import json
import os
import re
import time
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import requests
from dotenv import load_dotenv
from requests import RequestException


API = "https://api.github.com"
RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")
REPO_ALIASES = {
    "xgboost/xgboost": "dmlc/xgboost",
}
DISCOVERY_QUERIES = [
    "topic:machine-learning stars:>500",
    "topic:deep-learning stars:>500",
    "topic:llm stars:>300",
    "topic:agent stars:>200",
    "topic:data-visualization stars:>300",
    "topic:database stars:>500",
    "topic:kubernetes stars:>300",
    "topic:devops stars:>300",
    "topic:observability stars:>200",
    "topic:web-framework stars:>500",
    "topic:frontend stars:>500",
    "topic:backend stars:>500",
    "language:Python stars:>1000",
    "language:TypeScript stars:>1000",
    "language:Go stars:>1000",
    "language:Rust stars:>1000",
    "language:Java stars:>1000",
    "language:C++ stars:>1000",
    "China stars:>100",
    "India stars:>100",
    "Japan stars:>100",
    "Germany stars:>100",
    "France stars:>100",
    "United Kingdom stars:>100",
    "Canada stars:>100",
    "Netherlands stars:>100",
    "Australia stars:>100",
]
DEFAULT_DISCOVER_TARGET = 220
CITY_COORDS = {
    "San Francisco": ("United States", 37.7749, -122.4194),
    "New York": ("United States", 40.7128, -74.0060),
    "Beijing": ("China", 39.9042, 116.4074),
    "Shanghai": ("China", 31.2304, 121.4737),
    "London": ("United Kingdom", 51.5072, -0.1276),
    "Berlin": ("Germany", 52.5200, 13.4050),
    "Paris": ("France", 48.8566, 2.3522),
    "Bangalore": ("India", 12.9716, 77.5946),
    "Tokyo": ("Japan", 35.6762, 139.6503),
    "Toronto": ("Canada", 43.6532, -79.3832),
    "Amsterdam": ("Netherlands", 52.3676, 4.9041),
    "Sydney": ("Australia", -33.8688, 151.2093),
}
COUNTRY_ALIASES = {
    "usa": "United States",
    "united states": "United States",
    "new york": "United States",
    "san francisco": "United States",
    "china": "China",
    "beijing": "China",
    "shanghai": "China",
    "germany": "Germany",
    "berlin": "Germany",
    "france": "France",
    "paris": "France",
    "india": "India",
    "bangalore": "India",
    "japan": "Japan",
    "tokyo": "Japan",
    "uk": "United Kingdom",
    "united kingdom": "United Kingdom",
    "london": "United Kingdom",
    "canada": "Canada",
    "toronto": "Canada",
    "netherlands": "Netherlands",
    "amsterdam": "Netherlands",
    "australia": "Australia",
    "sydney": "Australia",
}


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def normalize_repo(repo: str) -> str:
    normalized = REPO_ALIASES.get(repo, repo)
    if normalized != repo:
        print(f"仓库名映射：{repo} -> {normalized}")
    return normalized


def read_projects(path: Path) -> list[str]:
    repos = []
    seen = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        repo = line.strip()
        if not repo or repo.startswith("#"):
            continue
        repo = normalize_repo(repo)
        if repo not in seen:
            repos.append(repo)
            seen.add(repo)
    return repos


def normalize_discovery_query(query: str, pushed_after: str) -> str:
    search_query = query.strip()
    lower = search_query.lower()
    if "pushed:" not in lower:
        search_query = f"{search_query} pushed:>={pushed_after}"
    if "fork:" not in lower:
        search_query = f"{search_query} fork:false"
    if "archived:" not in lower:
        search_query = f"{search_query} archived:false"
    return search_query


def discover_recent_repos(target: int, days: int, seeds: list[str], search_queries: list[str] | None = None) -> list[str]:
    if target <= 0:
        return seeds

    discovered: list[str] = []
    seen: set[str] = set()
    pushed_after = (utc_now() - timedelta(days=days)).date().isoformat()
    queries = [query.strip() for query in (search_queries or []) if query.strip()] or DISCOVERY_QUERIES
    is_custom_search = bool(search_queries)
    per_query = 100 if is_custom_search else max(10, min(50, target // max(len(queries), 1) + 5))
    pages_per_query = max(1, min(10, (target + per_query - 1) // per_query)) if is_custom_search else 1

    for query in queries:
        if len(discovered) >= target:
            break
        search_query = normalize_discovery_query(query, pushed_after)
        for page in range(1, pages_per_query + 1):
            if len(discovered) >= target:
                break
            try:
                data = get_json(
                    f"{API}/search/repositories",
                    {
                        "q": search_query,
                        "sort": "updated",
                        "order": "desc",
                        "per_page": per_query,
                        "page": page,
                    },
                )
            except Exception as exc:
                print(f"发现项目失败，跳过查询 {search_query} 第 {page} 页：{exc}")
                break
            items = data.get("items", [])
            if not items:
                break
            for item in items:
                repo = normalize_repo(item.get("full_name", ""))
                if repo and repo not in seen:
                    discovered.append(repo)
                    seen.add(repo)
                if len(discovered) >= target:
                    break

    github_discovered_count = len(discovered)
    for repo in seeds:
        if len(discovered) >= target:
            break
        if repo and repo not in seen:
            discovered.append(repo)
            seen.add(repo)

    print(f"项目发现完成：GitHub Search {github_discovered_count} 个，project_list 补充 {len(discovered) - github_discovered_count} 个，合计 {len(discovered)} 个")
    return discovered[:target]


def _records(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return pd.read_csv(path).fillna("").to_dict(orient="records")


def load_existing_snapshot(raw_path: Path, processed_dir: Path = PROCESSED_DIR) -> list[dict[str, Any]]:
    if raw_path.exists():
        try:
            data = json.loads(raw_path.read_text(encoding="utf-8"))
            items = data.get("items", [])
            if isinstance(items, list):
                return [item for item in items if isinstance(item, dict) and item.get("repo")]
            print(f"raw 快照 items 不是列表，忽略断点文件：{raw_path}")
        except Exception as exc:
            print(f"raw 快照读取失败，尝试从 processed CSV 恢复：{exc}")

    repos = _records(processed_dir / "repos.csv")
    if not repos:
        return []

    contributors_by_repo: dict[str, list[dict[str, Any]]] = {}
    for row in _records(processed_dir / "contributors.csv"):
        contributors_by_repo.setdefault(str(row.get("repo", "")), []).append(
            {
                "login": row.get("login", ""),
                "country": row.get("country", ""),
                "city": row.get("city", ""),
                "lat": row.get("lat") or None,
                "lon": row.get("lon") or None,
                "contributions": row.get("contributions", 0),
                "raw_location": row.get("raw_location", ""),
            }
        )

    issues_by_repo: dict[str, list[dict[str, Any]]] = {}
    for row in _records(processed_dir / "issues.csv"):
        issues_by_repo.setdefault(str(row.get("repo", "")), []).append(
            {
                "number": row.get("issue_id", ""),
                "title": row.get("title", ""),
                "state": row.get("state", ""),
                "created_at": row.get("created_at", ""),
                "closed_at": row.get("closed_at", ""),
            }
        )

    pulls_by_repo: dict[str, list[dict[str, Any]]] = {}
    for row in _records(processed_dir / "pulls.csv"):
        pulls_by_repo.setdefault(str(row.get("repo", "")), []).append(
            {
                "number": row.get("pr_id", ""),
                "title": row.get("title", ""),
                "state": row.get("state", ""),
                "created_at": row.get("created_at", ""),
                "closed_at": row.get("closed_at", ""),
                "merged_at": row.get("merged_at", ""),
            }
        )

    text_by_repo = {str(row.get("repo", "")): str(row.get("source_text", "")) for row in _records(processed_dir / "text_corpus.csv")}

    snapshot = []
    for row in repos:
        repo = str(row.get("repo", ""))
        if not repo:
            continue
        topics = str(row.get("topics", "")).split(";") if row.get("topics") else []
        snapshot.append(
            {
                "repo": repo,
                "repo_data": {
                    "owner": {"login": row.get("owner", repo.split("/")[0])},
                    "name": row.get("name", repo.split("/")[-1]),
                    "description": row.get("description", ""),
                    "stargazers_count": row.get("stars", 0),
                    "forks_count": row.get("forks", 0),
                    "subscribers_count": row.get("watchers", 0),
                    "watchers_count": row.get("watchers", 0),
                    "open_issues_count": row.get("open_issues", 0),
                    "language": row.get("language", "Unknown"),
                    "license": {"spdx_id": row.get("license", "Unknown")},
                    "created_at": row.get("created_at", ""),
                    "updated_at": row.get("updated_at", ""),
                    "pushed_at": row.get("pushed_at", ""),
                    "topics": topics,
                },
                "contributors": contributors_by_repo.get(repo, []),
                "issues": issues_by_repo.get(repo, []),
                "pulls": pulls_by_repo.get(repo, []),
                "commits": [],
                "readme": text_by_repo.get(repo, ""),
            }
        )
    print(f"已从 processed CSV 恢复断点快照：{len(snapshot)} 个项目")
    return snapshot


def append_star_history(repo_rows: list[dict[str, Any]], processed_dir: Path) -> None:
    history_path = processed_dir / "star_history.csv"
    new_rows = [
        {
            "repo": row["repo"],
            "stars": row["stars"],
            "forks": row["forks"],
            "open_issues": row["open_issues"],
            "collected_at": row["collected_at"],
        }
        for row in repo_rows
    ]
    history = pd.read_csv(history_path) if history_path.exists() else pd.DataFrame()
    merged = pd.concat([history, pd.DataFrame(new_rows)], ignore_index=True)
    merged = merged.drop_duplicates(["repo", "collected_at"], keep="last")
    merged.to_csv(history_path, index=False)


def headers() -> dict[str, str]:
    token = os.getenv("GITHUB_TOKEN", "").strip()
    value = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "OpenSourceLens",
    }
    if token:
        value["Authorization"] = f"Bearer {token}"
    return value


def get_json(url: str, params: dict[str, Any] | None = None, timeout: int = 30, retries: int = 4, backoff: float = 2.0) -> Any:
    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            response = requests.get(url, headers=headers(), params=params, timeout=timeout)
            if response.status_code == 403 and response.headers.get("X-RateLimit-Remaining") == "0":
                reset = int(response.headers.get("X-RateLimit-Reset", "0"))
                wait_seconds = max(0, reset - int(time.time())) + 2
                raise RuntimeError(f"GitHub API rate limit exceeded，请在 {wait_seconds} 秒后重试，或配置 GITHUB_TOKEN。")
            if response.status_code in {429, 500, 502, 503, 504} and attempt < retries:
                sleep_seconds = backoff * attempt
                print(f"请求暂时失败 {response.status_code}，{sleep_seconds:.1f}s 后重试：{url}")
                time.sleep(sleep_seconds)
                continue
            if response.status_code == 404:
                raise RuntimeError(f"GitHub 仓库或资源不存在：{url}")
            response.raise_for_status()
            return response.json()
        except (requests.exceptions.SSLError, requests.exceptions.ConnectionError, requests.exceptions.Timeout) as exc:
            last_error = exc
            if attempt >= retries:
                break
            sleep_seconds = backoff * attempt
            print(f"网络连接失败，{sleep_seconds:.1f}s 后重试 {attempt}/{retries}：{url}；原因：{exc}")
            time.sleep(sleep_seconds)
        except RequestException as exc:
            last_error = exc
            if attempt >= retries:
                break
            sleep_seconds = backoff * attempt
            print(f"GitHub 请求失败，{sleep_seconds:.1f}s 后重试 {attempt}/{retries}：{url}；原因：{exc}")
            time.sleep(sleep_seconds)
    raise RuntimeError(f"GitHub 请求多次失败：{url}；最后错误：{last_error}")


def search_count(query: str) -> int:
    data = get_json(f"{API}/search/issues", {"q": query, "per_page": 1})
    return int(data.get("total_count", 0))


def classify_issue(title: str) -> str:
    text = title.lower()
    rules = {
        "Bug": ["bug", "error", "exception", "crash", "fail", "wrong"],
        "Feature Request": ["feature", "request", "enhancement", "support", "add"],
        "Documentation": ["doc", "readme", "example", "tutorial"],
        "Installation": ["install", "build", "compile", "pip", "conda"],
        "Performance": ["slow", "performance", "memory", "latency", "speed"],
        "Compatibility": ["version", "compatible", "windows", "linux", "mac", "cuda"],
        "Question": ["how", "question", "why", "help", "usage"],
    }
    for label, words in rules.items():
        if any(word in text for word in words):
            return label
    return "Question"


def classify_commit(message: str) -> str:
    text = message.lower().strip()
    match = re.match(r"^([a-z]+)(\(.+?\))?:", text)
    if match and match.group(1) in {"fix", "feat", "docs", "refactor", "test", "perf", "chore"}:
        return match.group(1)
    for kind in ["fix", "feat", "docs", "refactor", "test", "perf", "chore"]:
        if text.startswith(kind) or f" {kind} " in text:
            return kind
    return "chore"


def infer_location(location: str) -> tuple[str, str, float | None, float | None]:
    text = (location or "").lower()
    for city, (country, lat, lon) in CITY_COORDS.items():
        if city.lower() in text:
            return country, city, lat, lon
    for key, country in COUNTRY_ALIASES.items():
        if key in text:
            city = next((name for name, data in CITY_COORDS.items() if data[0] == country), "")
            if city:
                _, lat, lon = CITY_COORDS[city]
                return country, city, lat, lon
            return country, "", None, None
    return "", "", None, None


def fetch_readme(repo: str) -> str:
    try:
        data = get_json(f"{API}/repos/{repo}/readme")
        raw = data.get("content", "")
        if data.get("encoding") == "base64" and raw:
            return base64.b64decode(raw).decode("utf-8", errors="ignore")[:12000]
    except Exception:
        return ""
    return ""


def fetch_repo(repo: str, since: str, contributor_limit: int, item_limit: int) -> dict[str, Any]:
    repo_data = get_json(f"{API}/repos/{repo}")
    contributors = get_json(f"{API}/repos/{repo}/contributors", {"per_page": min(contributor_limit, 100), "anon": "false"})
    contributor_profiles = []
    for item in contributors[:contributor_limit]:
        login = item.get("login", "")
        profile = {}
        if login:
            try:
                profile = get_json(f"{API}/users/{login}")
            except Exception:
                profile = {}
        location = profile.get("location", "")
        country, city, lat, lon = infer_location(location)
        contributor_profiles.append(
            {
                "login": login,
                "country": country,
                "city": city,
                "lat": lat,
                "lon": lon,
                "contributions": item.get("contributions", 0),
                "raw_location": location,
            }
        )

    issues = get_json(f"{API}/repos/{repo}/issues", {"state": "all", "since": since, "per_page": item_limit, "sort": "updated", "direction": "desc"})
    issue_rows = [item for item in issues if "pull_request" not in item]
    pull_rows = get_json(f"{API}/repos/{repo}/pulls", {"state": "all", "per_page": item_limit, "sort": "updated", "direction": "desc"})
    commits = get_json(f"{API}/repos/{repo}/commits", {"since": since, "per_page": item_limit})
    readme = fetch_readme(repo)
    return {
        "repo": repo,
        "repo_data": repo_data,
        "contributors": contributor_profiles,
        "issues": issue_rows,
        "pulls": pull_rows,
        "commits": commits,
        "readme": readme,
    }


def write_outputs(snapshot: list[dict[str, Any]], raw_path: Path, processed_dir: Path, failures: list[dict[str, str]] | None = None) -> None:
    repo_rows, contributor_rows, geo_rows, issue_rows, pull_rows, text_rows = [], [], [], [], [], []
    for item in snapshot:
        repo = item["repo"]
        data = item["repo_data"]
        contributors = item["contributors"]
        countries = [row["country"] for row in contributors if row.get("country")]
        cities = [row["city"] for row in contributors if row.get("city")]
        recent_issues = item["issues"]
        recent_pulls = item["pulls"]
        closed_issues = [row for row in recent_issues if row.get("state") == "closed"]
        merged_pulls = [row for row in recent_pulls if row.get("merged_at")]
        commit_types = [classify_commit(commit.get("commit", {}).get("message", "")) for commit in item["commits"]]
        main_commit_type = Counter(commit_types).most_common(1)[0][0] if commit_types else "chore"
        repo_rows.append(
            {
                "repo": repo,
                "owner": data.get("owner", {}).get("login", repo.split("/")[0]),
                "name": data.get("name", repo.split("/")[-1]),
                "description": data.get("description", ""),
                "stars": data.get("stargazers_count", 0),
                "forks": data.get("forks_count", 0),
                "watchers": data.get("subscribers_count", data.get("watchers_count", 0)),
                "open_issues": data.get("open_issues_count", 0),
                "language": data.get("language", "Unknown"),
                "license": (data.get("license") or {}).get("spdx_id", "Unknown"),
                "created_at": data.get("created_at", ""),
                "updated_at": data.get("updated_at", ""),
                "pushed_at": data.get("pushed_at", ""),
                "topics": ";".join(data.get("topics", [])),
                "contributors": len(contributors),
                "commits_recent": len(item["commits"]),
                "issues_recent": len(recent_issues),
                "prs_recent": len(recent_pulls),
                "issue_close_rate": len(closed_issues) / max(len(recent_issues), 1),
                "pr_merge_rate": len(merged_pulls) / max(len(recent_pulls), 1),
                "country_count": len(set(countries)),
                "city_count": len(set(cities)),
                "data_source": "github_api",
                "collected_at": utc_now().isoformat(),
            }
        )
        for row in contributors:
            base = {
                "repo": repo,
                "login": row.get("login", ""),
                "country": row.get("country", ""),
                "city": row.get("city", ""),
                "lat": row.get("lat"),
                "lon": row.get("lon"),
                "contributions": row.get("contributions", 0),
            }
            contributor_rows.append({**base, "raw_location": row.get("raw_location", "")})
            if base["country"] and base["city"]:
                geo_rows.append(base)
        for row in recent_issues:
            issue_rows.append(
                {
                    "repo": repo,
                    "issue_id": row.get("number"),
                    "title": row.get("title", ""),
                    "state": row.get("state", ""),
                    "created_at": row.get("created_at", ""),
                    "closed_at": row.get("closed_at", ""),
                    "issue_type": classify_issue(row.get("title", "")),
                }
            )
        for row in recent_pulls:
            pull_rows.append(
                {
                    "repo": repo,
                    "pr_id": row.get("number"),
                    "title": row.get("title", ""),
                    "state": row.get("state", ""),
                    "created_at": row.get("created_at", ""),
                    "closed_at": row.get("closed_at", ""),
                    "merged_at": row.get("merged_at", ""),
                }
            )
        text_rows.append(
            {
                "repo": repo,
                "source_text": f"{data.get('description', '')}\n{';'.join(data.get('topics', []))}\n{item['readme'][:6000]}",
                "readme_keywords": ";".join(data.get("topics", [])),
                "commit_type": main_commit_type,
            }
        )

    raw_path.parent.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)
    raw_path.write_text(json.dumps({"collected_at": utc_now().isoformat(), "items": snapshot}, ensure_ascii=False, indent=2), encoding="utf-8")
    pd.DataFrame(repo_rows).to_csv(processed_dir / "repos.csv", index=False)
    pd.DataFrame(repo_rows).to_csv(processed_dir / "scores.csv", index=False)
    pd.DataFrame(contributor_rows).to_csv(processed_dir / "contributors.csv", index=False)
    pd.DataFrame(geo_rows).to_csv(processed_dir / "geo_contributors.csv", index=False)
    pd.DataFrame(issue_rows).to_csv(processed_dir / "issues.csv", index=False)
    pd.DataFrame(pull_rows).to_csv(processed_dir / "pulls.csv", index=False)
    pd.DataFrame(text_rows).to_csv(processed_dir / "text_corpus.csv", index=False)
    append_star_history(repo_rows, processed_dir)
    metadata = {
        "source": "github_api",
        "collected_at": utc_now().isoformat(),
        "repo_count": len(repo_rows),
        "failed_repo_count": len(failures or []),
        "failed_repos": failures or [],
        "next_steps": ["scripts/clean_data.py", "scripts/build_features.py", "scripts/train_models.py", "scripts/build_text_features.py"],
    }
    (processed_dir / "refresh_metadata.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    load_dotenv()
    parser = argparse.ArgumentParser(description="采集真实 GitHub 数据，写入 data/processed/，不在 Reflex 页面中调用。")
    parser.add_argument("--projects", type=Path, default=Path("data/project_list.txt"))
    parser.add_argument("--raw", type=Path, default=RAW_DIR / "github_snapshot.json")
    parser.add_argument("--processed", type=Path, default=PROCESSED_DIR)
    parser.add_argument("--days", type=int, default=90)
    parser.add_argument("--contributors", type=int, default=40)
    parser.add_argument("--items", type=int, default=60)
    parser.add_argument("--sleep", type=float, default=0.2)
    parser.add_argument("--strict", action="store_true", help="任一仓库采集失败时立即中断。默认会跳过失败仓库并保存已采集结果。")
    parser.add_argument("--no-resume", action="store_true", help="不读取既有 data/raw/github_snapshot.json，重新采集并覆盖输出。")
    parser.add_argument("--refresh-existing", action="store_true", help="即使 raw 快照中已有该仓库，也重新采集更新。")
    parser.add_argument("--discover-target", type=int, default=DEFAULT_DISCOVER_TARGET, help="通过 GitHub Search 自动发现最近活跃项目，扩展到指定项目数；0 表示只使用 project_list。")
    parser.add_argument("--discover-days", type=int, default=30, help="自动发现项目时，只选择最近 N 天更新过的仓库。")
    parser.add_argument("--search-query", action="append", default=[], help="自定义 GitHub Search 查询，可重复传入；未传时使用内置多主题发现查询。")
    parser.add_argument("--seed-only", action="store_true", help="只采集 data/project_list.txt 中的仓库，不使用 GitHub Search 自动发现。")
    args = parser.parse_args()

    since = (utc_now() - timedelta(days=args.days)).isoformat()
    snapshot = [] if args.no_resume else load_existing_snapshot(args.raw)
    snapshot_by_repo = {item.get("repo"): item for item in snapshot if item.get("repo")}
    failures = []
    seed_projects = read_projects(args.projects)
    if args.seed_only or args.discover_target <= 0:
        projects = seed_projects
    else:
        projects = discover_recent_repos(args.discover_target, args.discover_days, seed_projects, args.search_query)
    for repo in projects:
        if repo in snapshot_by_repo and not args.refresh_existing:
            print(f"跳过已采集 {repo}")
            continue
        print(f"采集 {repo}")
        try:
            item = fetch_repo(repo, since, args.contributors, args.items)
            snapshot_by_repo[repo] = item
            snapshot = list(snapshot_by_repo.values())
            write_outputs(snapshot, args.raw, args.processed, failures)
            print(f"已保存进度：成功 {len(snapshot)} 个，失败 {len(failures)} 个")
        except Exception as exc:
            message = str(exc)
            failures.append({"repo": repo, "error": message})
            print(f"跳过 {repo}：{message}")
            if snapshot:
                write_outputs(snapshot, args.raw, args.processed, failures)
            if args.strict:
                raise
        time.sleep(args.sleep)
    if not snapshot:
        raise RuntimeError("所有仓库都采集失败，没有可写入的数据。请检查网络、代理或 GITHUB_TOKEN。")
    write_outputs(snapshot, args.raw, args.processed, failures)
    print(f"真实 GitHub 数据已写入 {args.processed}；成功 {len(snapshot)} 个，失败 {len(failures)} 个")


if __name__ == "__main__":
    main()
