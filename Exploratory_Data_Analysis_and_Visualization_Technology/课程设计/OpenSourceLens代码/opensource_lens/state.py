from __future__ import annotations

from datetime import datetime

import pandas as pd
import plotly.graph_objects as go
import reflex as rx

from .utils.github_realtime import fetch_star_rank_projects, fetch_trending_projects
from .utils.make_charts import (
    make_anomaly_scatter,
    make_city_bubble_map,
    make_city_top_bar,
    make_cluster_average_heatmap,
    make_cluster_radar,
    make_cluster_scatter,
    make_cluster_profile_bar,
    make_correlation_heatmap,
    make_country_top_bar,
    make_created_year_bar,
    make_fork_bar,
    make_issue_status_chart,
    make_issue_topic_bar,
    make_language_distribution,
    make_language_score_box,
    make_multi_project_radar,
    make_metric_distribution,
    make_first_year_star_bar,
    make_project_country_heatmap,
    make_project_radar,
    make_pull_status_chart,
    make_quadrant_scatter,
    make_rate_compare_bar,
    make_recent_activity_bar,
    make_risk_project_bar,
    make_score_compare_bar,
    make_score_distribution,
    make_similarity_heatmap,
    make_star_bar,
    make_star_growth_bar,
    make_star_fork_scatter,
    make_text_embedding_scatter,
    make_world_map,
    make_commit_type_bar,
    make_ecosystem_bubble,
    make_language_treemap,
    make_score_heatmap,
    make_star_rank_bar,
    make_star_rank_language_bar,
    make_snapshot_coverage_bar,
    make_time_series_change_bar,
    make_time_series_line,
    make_trending_language_bar,
    make_trending_star_bar,
)
from .utils.load_data import (
    dataframe_records,
    load_cluster_profiles,
    load_geo_contributors,
    load_issues,
    load_ml_results,
    load_model_metrics,
    load_pulls,
    load_refresh_metadata,
    load_scores,
    load_star_growth,
    load_star_history,
    load_text_results,
    load_text_similarity,
    processed_fingerprint,
)


def _index_rows(rows: list[dict], key: str = "repo") -> dict[str, list[int]]:
    index: dict[str, list[int]] = {}
    for i, row in enumerate(rows):
        value = str(row.get(key, ""))
        if value:
            index.setdefault(value, []).append(i)
    return index


def _index_one_row(rows: list[dict], key: str = "repo") -> dict[str, int]:
    index: dict[str, int] = {}
    for i, row in enumerate(rows):
        value = str(row.get(key, ""))
        if value and value not in index:
            index[value] = i
    return index


def _indexed_rows(rows: list[dict], index: dict[str, list[int]], value: str, limit: int = 800) -> list[dict]:
    indexes = index.get(value, [])
    return [rows[i] for i in indexes[:limit] if i < len(rows)]


def _display_source(source: str, has_rows: bool) -> str:
    if source == "github_api":
        return "GitHub API"
    if source == "demo":
        return "Demo 数据"
    if source:
        return source
    return "本地 CSV" if has_rows else "未知"


_CHART_CACHE: dict[str, go.Figure] = {}
_CHART_CACHE_LIMIT = 420
_DISTRIBUTION_METRICS = ["Stars", "Forks", "Open Issues", "贡献者", "热度评分", "活跃度评分", "健康度评分", "国际化评分"]
_SCORE_METRICS = ["热度评分", "活跃度评分", "健康度评分", "国际化评分"]


def _cached_chart(key: str, builder) -> go.Figure:
    chart = _CHART_CACHE.get(key)
    if chart is not None:
        return chart
    chart = builder()
    if len(_CHART_CACHE) >= _CHART_CACHE_LIMIT:
        _CHART_CACHE.clear()
    _CHART_CACHE[key] = chart
    return chart


def _dashboard_rows(
    rows: list[dict],
    language: str,
    keyword: str = "",
    star_min: int = 0,
    star_max: int = 1000000,
    health_min: float = 0.0,
    activity_min: float = 0.0,
) -> list[dict]:
    filtered = []
    needle = keyword.lower().strip()
    for row in rows:
        if language != "全部语言" and row.get("language") != language:
            continue
        if float(row.get("stars", 0) or 0) < star_min:
            continue
        if star_max and float(row.get("stars", 0) or 0) > star_max:
            continue
        if float(row.get("health_score", 0) or 0) < health_min:
            continue
        if float(row.get("activity_score", 0) or 0) < activity_min:
            continue
        haystack = f"{row.get('repo', '')} {row.get('description', '')}".lower()
        if needle and needle not in haystack:
            continue
        filtered.append(row)
    return filtered


def _dashboard_chart_key(
    chart_name: str,
    fingerprint: str,
    language: str,
    keyword: str = "",
    star_min: int = 0,
    star_max: int = 1000000,
    health_min: float = 0.0,
    activity_min: float = 0.0,
) -> str:
    return f"dashboard:{chart_name}:{fingerprint}:{language}:{keyword}:{star_min}:{star_max}:{health_min}:{activity_min}"


def _top_languages(rows: list[dict], limit: int = 3) -> list[str]:
    counts: dict[str, int] = {}
    for row in rows:
        language = str(row.get("language", "") or "Unknown")
        if language == "全部语言":
            continue
        counts[language] = counts.get(language, 0) + 1
    return [language for language, _ in sorted(counts.items(), key=lambda item: item[1], reverse=True)[:limit]]


def _language_prewarm_values(rows: list[dict]) -> list[str]:
    values = ["全部语言"]
    for language in _top_languages(rows, limit=3):
        if language not in values:
            values.append(language)
    return values


def _top_countries(rows: list[dict], limit: int = 3) -> list[str]:
    totals: dict[str, float] = {}
    for row in rows:
        country = str(row.get("country", "") or "")
        if not country:
            continue
        totals[country] = totals.get(country, 0) + float(row.get("contributions", 1) or 1)
    return [country for country, _ in sorted(totals.items(), key=lambda item: item[1], reverse=True)[:limit]]


def _country_prewarm_values(rows: list[dict]) -> list[str]:
    values = ["全部国家"]
    for country in _top_countries(rows, limit=3):
        if country not in values:
            values.append(country)
    return values


def _build_dashboard_chart(chart_name: str, rows: list[dict]) -> go.Figure:
    df = pd.DataFrame(rows)
    builders = {
        "star_bar": make_star_bar,
        "first_year_star": make_first_year_star_bar,
        "fork_bar": make_fork_bar,
        "star_fork": make_star_fork_scatter,
        "language": make_language_distribution,
        "created_year": make_created_year_bar,
        "quadrant": make_quadrant_scatter,
        "ecosystem": make_ecosystem_bubble,
        "language_treemap": make_language_treemap,
        "score_heatmap": make_score_heatmap,
    }
    return builders[chart_name](df)


def _prewarm_dashboard_language_charts(rows: list[dict], fingerprint: str) -> None:
    chart_names = [
        "ecosystem",
        "language_treemap",
        "score_heatmap",
        "language",
        "star_fork",
        "star_bar",
        "first_year_star",
    ]
    for language in _language_prewarm_values(rows):
        filtered = _dashboard_rows(rows, language)
        for chart_name in chart_names:
            key = _dashboard_chart_key(chart_name, fingerprint, language)
            _cached_chart(key, lambda chart_name=chart_name, filtered=filtered: _build_dashboard_chart(chart_name, filtered))


def _statistics_chart_key(
    chart_name: str,
    fingerprint: str,
    language: str,
    keyword: str = "",
    star_min: int = 0,
    star_max: int = 1000000,
    health_min: float = 0.0,
    activity_min: float = 0.0,
    metric: str = "",
) -> str:
    return f"statistics:{chart_name}:{fingerprint}:{language}:{keyword}:{star_min}:{star_max}:{health_min}:{activity_min}:{metric}"


def _build_statistics_chart(chart_name: str, rows: list[dict], metric: str = "") -> go.Figure:
    df = pd.DataFrame(rows)
    if chart_name == "metric_distribution":
        return make_metric_distribution(df, metric or "Stars")
    if chart_name == "score_distribution":
        return make_score_distribution(df)
    if chart_name == "correlation":
        return make_correlation_heatmap(df)
    if chart_name == "language_score":
        return make_language_score_box(df, metric or "健康度评分")
    raise ValueError(f"Unknown statistics chart: {chart_name}")


def _prewarm_statistics_language_charts(rows: list[dict], fingerprint: str) -> None:
    for language in _language_prewarm_values(rows):
        filtered = _dashboard_rows(rows, language)
        for metric in _DISTRIBUTION_METRICS:
            key = _statistics_chart_key("metric_distribution", fingerprint, language, metric=metric)
            _cached_chart(key, lambda filtered=filtered, metric=metric: _build_statistics_chart("metric_distribution", filtered, metric))
        for chart_name in ["score_distribution", "correlation"]:
            key = _statistics_chart_key(chart_name, fingerprint, language)
            _cached_chart(key, lambda filtered=filtered, chart_name=chart_name: _build_statistics_chart(chart_name, filtered))
        for metric in _SCORE_METRICS:
            key = _statistics_chart_key("language_score", fingerprint, language, metric=metric)
            _cached_chart(key, lambda filtered=filtered, metric=metric: _build_statistics_chart("language_score", filtered, metric))


def _geo_rows(rows: list[dict], repo: str = "全部项目", country: str = "全部国家") -> list[dict]:
    filtered = []
    for row in rows:
        if repo and repo != "全部项目" and row.get("repo") != repo:
            continue
        if country and country != "全部国家" and row.get("country") != country:
            continue
        filtered.append(row)
    return filtered


def _geo_chart_key(chart_name: str, fingerprint: str, repo: str = "全部项目", country: str = "全部国家") -> str:
    return f"geo:{chart_name}:{fingerprint}:{repo}:{country}"


def _repo_languages(rows: list[dict]) -> dict[str, str]:
    return {str(row.get("repo", "")): str(row.get("language", "") or "Unknown") for row in rows if row.get("repo")}


def _geo_language_rows(geo_rows: list[dict], score_rows: list[dict], language: str = "全部语言") -> list[dict]:
    if not language or language == "全部语言":
        return geo_rows
    repo_languages = _repo_languages(score_rows)
    return [row for row in geo_rows if repo_languages.get(str(row.get("repo", ""))) == language]


def _geo_language_chart_key(chart_name: str, fingerprint: str, language: str = "全部语言") -> str:
    return f"geo-language:{chart_name}:{fingerprint}:{language}"


def _build_geo_chart(chart_name: str, rows: list[dict]) -> go.Figure:
    df = pd.DataFrame(rows)
    builders = {
        "world": make_world_map,
        "city_bubble": make_city_bubble_map,
        "country_top": make_country_top_bar,
        "city_top": make_city_top_bar,
        "project_country": make_project_country_heatmap,
    }
    return builders[chart_name](df)


def _prewarm_geo_country_charts(rows: list[dict], fingerprint: str, repo: str = "全部项目") -> None:
    chart_names = ["world", "city_bubble", "country_top", "city_top", "project_country"]
    repo_rows = _geo_rows(rows, repo, "全部国家")
    for country in _country_prewarm_values(repo_rows):
        filtered = _geo_rows(rows, repo, country)
        for chart_name in chart_names:
            key = _geo_chart_key(chart_name, fingerprint, repo, country)
            _cached_chart(key, lambda chart_name=chart_name, filtered=filtered: _build_geo_chart(chart_name, filtered))


def _prewarm_geo_language_charts(geo_rows: list[dict], score_rows: list[dict], fingerprint: str) -> None:
    for language in _language_prewarm_values(score_rows):
        filtered = _geo_language_rows(geo_rows, score_rows, language)
        key = _geo_language_chart_key("world", fingerprint, language)
        _cached_chart(key, lambda filtered=filtered: _build_geo_chart("world", filtered))


class LensState(rx.State):
    selected_repo: str = ""
    selected_repos: list[str] = []
    compare_candidate_repo: str = ""
    selected_geo_repo: str = "全部项目"
    selected_language: str = "全部语言"
    selected_country: str = "全部国家"
    selected_distribution_metric: str = "Stars"
    selected_trend_metric: str = "Stars"
    selected_trend_repos: list[str] = []
    trend_candidate_repo: str = ""
    star_min: int = 0
    star_max: int = 1000000
    health_min: float = 0.0
    activity_min: float = 0.0
    search_keyword: str = ""
    last_update_time: str = ""
    realtime_growth_status: str = "尚未采集。点击按钮后将实时读取 GitHub Trending。"
    realtime_repo_limit: str = "10"
    realtime_trending_language: str = "全部语言"
    realtime_trending_since: str = "今日"
    realtime_growth_progress: int = 0
    realtime_growth_done: int = 0
    realtime_growth_total: int = 0
    realtime_growth_running: bool = False
    star_growth_version: str = ""
    star_rank_status: str = "尚未查询。点击按钮后将实时读取 GitHub Stars 排行。"
    star_rank_limit: str = "30"
    star_rank_query: str = "stars:>1000"
    star_rank_language: str = "全部语言"
    star_rank_running: bool = False
    star_rank_progress: int = 0
    star_rank_version: str = ""
    trending_version: str = ""
    status_message: str = "未加载数据"
    data_source: str = "未知"
    data_collected_at: str = "暂无"
    model_trained_at: str = "暂无"
    local_refreshed_at: str = "暂无"
    data_fingerprint: str = ""

    _scores: list[dict] = []
    _geo_rows: list[dict] = []
    _issue_rows: list[dict] = []
    _pull_rows: list[dict] = []
    _ml_rows: list[dict] = []
    _model_metrics_rows: list[dict] = []
    _cluster_profile_rows: list[dict] = []
    _text_rows: list[dict] = []
    _text_similarity_rows: list[dict] = []
    _star_growth_rows: list[dict] = []
    _star_history_rows: list[dict] = []
    _star_rank_rows: list[dict] = []
    _trending_rows: list[dict] = []
    _score_index_by_repo: dict[str, int] = {}
    _issue_index_by_repo: dict[str, list[int]] = {}
    _pull_index_by_repo: dict[str, list[int]] = {}
    _geo_index_by_repo: dict[str, list[int]] = {}
    _geo_index_by_country: dict[str, list[int]] = {}

    def load_data(self):
        scores = load_scores()
        self._scores = dataframe_records(scores)
        self._geo_rows = dataframe_records(load_geo_contributors())
        self._issue_rows = dataframe_records(load_issues())
        self._pull_rows = dataframe_records(load_pulls())
        self._ml_rows = dataframe_records(load_ml_results())
        self._model_metrics_rows = dataframe_records(load_model_metrics())
        self._cluster_profile_rows = dataframe_records(load_cluster_profiles())
        self._text_rows = dataframe_records(load_text_results())
        self._text_similarity_rows = dataframe_records(load_text_similarity())
        self._star_growth_rows = dataframe_records(load_star_growth())
        self._star_history_rows = dataframe_records(load_star_history())
        self._score_index_by_repo = _index_one_row(self._scores)
        self._issue_index_by_repo = _index_rows(self._issue_rows)
        self._pull_index_by_repo = _index_rows(self._pull_rows)
        self._geo_index_by_repo = _index_rows(self._geo_rows)
        self._geo_index_by_country = _index_rows(self._geo_rows, "country")
        metadata = load_refresh_metadata()
        repos = [str(row.get("repo", "")) for row in self._scores if row.get("repo")]
        first_repo = repos[0] if repos else ""
        if self.selected_repo not in repos:
            self.selected_repo = first_repo
        self.selected_repos = [repo for repo in self.selected_repos if repo in repos][:5]
        self.selected_trend_repos = [repo for repo in self.selected_trend_repos if repo in repos][:6]
        if self.compare_candidate_repo not in repos:
            self.compare_candidate_repo = ""
        if self.trend_candidate_repo not in repos:
            self.trend_candidate_repo = ""
        self.local_refreshed_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.last_update_time = self.local_refreshed_at
        self.data_source = _display_source(str(metadata.get("source", "")), bool(self._scores))
        self.data_collected_at = str(metadata.get("collected_at", "暂无"))
        self.model_trained_at = str(metadata.get("trained_at", "暂无"))
        new_fingerprint = processed_fingerprint()
        if new_fingerprint != self.data_fingerprint:
            _CHART_CACHE.clear()
        self.data_fingerprint = new_fingerprint
        _prewarm_dashboard_language_charts(self._scores, self.data_fingerprint)
        _prewarm_statistics_language_charts(self._scores, self.data_fingerprint)
        _prewarm_geo_country_charts(self._geo_rows, self.data_fingerprint)
        _prewarm_geo_language_charts(self._geo_rows, self._scores, self.data_fingerprint)
        self.status_message = f"已从 data/processed 加载 {len(self._scores)} 个项目" if self._scores else "未找到 processed 数据，请先运行 README 中的数据脚本"

    def refresh_data(self):
        self.load_data()

    def refresh_if_changed(self):
        current = processed_fingerprint()
        if current and current != self.data_fingerprint:
            self.load_data()
            self.status_message = "检测到本地 processed 数据变化，已重新加载"
        else:
            self.local_refreshed_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.status_message = "本地数据暂无变化"

    def set_selected_repo(self, value: str):
        self.selected_repo = value

    def select_compare_repo(self, value: str):
        self.compare_candidate_repo = value

    def set_selected_repos(self, value: list[str]):
        self.selected_repos = value[:5]

    def add_compare_repo(self):
        repo = self.compare_candidate_repo
        if not repo or repo == "全部项目":
            return
        if repo in self.selected_repos:
            return
        if len(self.selected_repos) >= 5:
            self.selected_repos = self.selected_repos[1:]
        self.selected_repos.append(repo)

    def clear_compare_repos(self):
        self.selected_repos = []
        self.compare_candidate_repo = ""

    def set_selected_language(self, value: str):
        self.selected_language = value

    def set_selected_country(self, value: str):
        self.selected_country = value

    def set_selected_geo_repo(self, value: str):
        self.selected_geo_repo = value or "全部项目"
        _prewarm_geo_country_charts(self._geo_rows, self.data_fingerprint, self.selected_geo_repo)

    def set_selected_distribution_metric(self, value: str):
        self.selected_distribution_metric = value or "Stars"

    def set_selected_trend_metric(self, value: str):
        self.selected_trend_metric = value or "Stars"

    def select_trend_repo(self, value: str):
        self.trend_candidate_repo = value

    def add_trend_repo(self):
        repo = self.trend_candidate_repo
        if not repo or repo == "全部项目":
            return
        if repo in self.selected_trend_repos:
            return
        if len(self.selected_trend_repos) >= 6:
            self.selected_trend_repos = self.selected_trend_repos[1:]
        self.selected_trend_repos.append(repo)

    def clear_trend_repos(self):
        self.selected_trend_repos = []
        self.trend_candidate_repo = ""

    def set_search_keyword(self, value: str):
        self.search_keyword = value

    def set_score_filters(self, health_min: float, activity_min: float):
        self.health_min = health_min
        self.activity_min = activity_min

    def set_star_min(self, value: str | int):
        self.star_min = int(float(value or 0))

    def set_star_max(self, value: str | int):
        self.star_max = int(float(value or 0))

    def set_health_min(self, value: str | float):
        self.health_min = float(value or 0)

    def set_activity_min(self, value: str | float):
        self.activity_min = float(value or 0)

    def set_realtime_repo_limit(self, value: str):
        self.realtime_repo_limit = value

    def set_realtime_trending_language(self, value: str):
        self.realtime_trending_language = value or "全部语言"

    def set_realtime_trending_since(self, value: str):
        self.realtime_trending_since = value or "今日"

    def set_star_rank_limit(self, value: str):
        self.star_rank_limit = value or "30"

    def set_star_rank_query(self, value: str):
        self.star_rank_query = value or "stars:>1000"

    def set_star_rank_language(self, value: str):
        self.star_rank_language = value or "全部语言"

    @rx.var(cache=True)
    def repo_options(self) -> list[str]:
        _ = self.data_fingerprint
        return [str(row.get("repo", "")) for row in self._scores]

    @rx.var(cache=True)
    def geo_repo_options(self) -> list[str]:
        return ["全部项目"] + self.repo_options

    @rx.var(cache=True)
    def language_options(self) -> list[str]:
        _ = self.data_fingerprint
        return ["全部语言"] + sorted({str(row.get("language", "Unknown")) for row in self._scores})

    @rx.var(cache=True)
    def country_options(self) -> list[str]:
        _ = self.data_fingerprint
        return ["全部国家"] + sorted({str(row.get("country", "")) for row in self._geo_rows if row.get("country")})

    def _quick_language_value(self, index: int) -> str:
        values = _language_prewarm_values(self._scores)
        return values[index] if index < len(values) else ""

    def _quick_country_value(self, index: int) -> str:
        rows = _geo_rows(self._geo_rows, self.selected_geo_repo, "全部国家")
        values = _country_prewarm_values(rows)
        return values[index] if index < len(values) else ""

    def _dashboard_quick_language_chart(self, index: int, chart_name: str) -> go.Figure:
        language = self._quick_language_value(index)
        if not language:
            return go.Figure()
        rows = _dashboard_rows(self._scores, language, self.search_keyword, self.star_min, self.star_max, self.health_min, self.activity_min)
        key = _dashboard_chart_key(chart_name, self.data_fingerprint, language, self.search_keyword, self.star_min, self.star_max, self.health_min, self.activity_min)
        return _cached_chart(key, lambda: _build_dashboard_chart(chart_name, rows))

    def _geo_quick_country_chart(self, index: int, chart_name: str) -> go.Figure:
        country = self._quick_country_value(index)
        if not country:
            return go.Figure()
        rows = _geo_rows(self._geo_rows, self.selected_geo_repo, country)
        key = _geo_chart_key(chart_name, self.data_fingerprint, self.selected_geo_repo, country)
        return _cached_chart(key, lambda: _build_geo_chart(chart_name, rows))

    def _dashboard_quick_language_key(self, index: int, chart_name: str) -> str:
        return _dashboard_chart_key(chart_name, self.data_fingerprint, self._quick_language_value(index), self.search_keyword, self.star_min, self.star_max, self.health_min, self.activity_min)

    def _geo_quick_country_key(self, index: int, chart_name: str) -> str:
        return _geo_chart_key(chart_name, self.data_fingerprint, self.selected_geo_repo, self._quick_country_value(index))

    def _geo_quick_language_chart(self, index: int, chart_name: str) -> go.Figure:
        language = self._quick_language_value(index)
        if not language:
            return go.Figure()
        rows = _geo_language_rows(self._geo_rows, self._scores, language)
        key = _geo_language_chart_key(chart_name, self.data_fingerprint, language)
        return _cached_chart(key, lambda: _build_geo_chart(chart_name, rows))

    def _geo_quick_language_key(self, index: int, chart_name: str) -> str:
        return _geo_language_chart_key(chart_name, self.data_fingerprint, self._quick_language_value(index))

    @rx.var(cache=True)
    def quick_language_all_label(self) -> str:
        return self._quick_language_value(0) or "全部语言"

    @rx.var(cache=True)
    def quick_language_1_label(self) -> str:
        return self._quick_language_value(1) or "语言 1"

    @rx.var(cache=True)
    def quick_language_2_label(self) -> str:
        return self._quick_language_value(2) or "语言 2"

    @rx.var(cache=True)
    def quick_language_3_label(self) -> str:
        return self._quick_language_value(3) or "语言 3"

    @rx.var(cache=True)
    def quick_country_all_label(self) -> str:
        return self._quick_country_value(0) or "全部国家"

    @rx.var(cache=True)
    def quick_country_1_label(self) -> str:
        return self._quick_country_value(1) or "国家 1"

    @rx.var(cache=True)
    def quick_country_2_label(self) -> str:
        return self._quick_country_value(2) or "国家 2"

    @rx.var(cache=True)
    def quick_country_3_label(self) -> str:
        return self._quick_country_value(3) or "国家 3"

    @rx.var(cache=True)
    def filtered_scores(self) -> list[dict]:
        _ = self.data_fingerprint
        rows = []
        keyword = self.search_keyword.lower().strip()
        for row in self._scores:
            if self.selected_language != "全部语言" and row.get("language") != self.selected_language:
                continue
            if float(row.get("stars", 0) or 0) < self.star_min:
                continue
            if self.star_max and float(row.get("stars", 0) or 0) > self.star_max:
                continue
            if float(row.get("health_score", 0) or 0) < self.health_min:
                continue
            if float(row.get("activity_score", 0) or 0) < self.activity_min:
                continue
            haystack = f"{row.get('repo', '')} {row.get('description', '')}".lower()
            if keyword and keyword not in haystack:
                continue
            rows.append(row)
        return rows

    @rx.var(cache=True)
    def filtered_scores_preview(self) -> list[dict]:
        return sorted(self.filtered_scores, key=lambda row: float(row.get("stars", 0) or 0), reverse=True)[:80]

    @rx.var(cache=True)
    def dashboard_metrics(self) -> list[dict]:
        rows = self.filtered_scores
        geo = self._geo_rows
        if not rows:
            return [
                {"label": "项目总数", "value": "0", "hint": "请先生成数据"},
                {"label": "总 Stars", "value": "0", "hint": ""},
                {"label": "总 Forks", "value": "0", "hint": ""},
                {"label": "总贡献者", "value": "0", "hint": ""},
            ]
        countries = {str(row.get("country", "")) for row in geo if row.get("country")}
        return [
            {"label": "项目总数", "value": str(len(rows)), "hint": "当前筛选结果"},
            {"label": "总 Stars", "value": f"{int(sum(float(row.get('stars', 0) or 0) for row in rows)):,}", "hint": "项目热度总量"},
            {"label": "总 Forks", "value": f"{int(sum(float(row.get('forks', 0) or 0) for row in rows)):,}", "hint": "社区复用规模"},
            {"label": "总贡献者", "value": f"{int(sum(float(row.get('contributors', 0) or 0) for row in rows)):,}", "hint": "累计贡献者"},
            {"label": "覆盖国家数", "value": str(len(countries) or int(max(float(row.get('country_count', 0) or 0) for row in rows))), "hint": "地域覆盖"},
            {"label": "平均健康度评分", "value": f"{sum(float(row.get('health_score', 0) or 0) for row in rows) / len(rows):.1%}", "hint": "越高越稳定"},
            {"label": "平均活跃度评分", "value": f"{sum(float(row.get('activity_score', 0) or 0) for row in rows) / len(rows):.1%}", "hint": "近期活跃程度"},
            {"label": "数据更新时间", "value": self.local_refreshed_at or "暂无", "hint": "本地加载时间"},
        ]

    @rx.var(cache=True)
    def selected_project_row(self) -> dict:
        _ = (self.data_fingerprint, self.selected_repo)
        index = self._score_index_by_repo.get(self.selected_repo)
        if index is not None and index < len(self._scores):
            return self._scores[index]
        return self._scores[0] if self._scores else {}

    @rx.var(cache=True)
    def selected_project_metrics(self) -> list[dict]:
        row = self.selected_project_row
        if not row:
            return [{"label": "项目", "value": "暂无数据", "hint": "请先生成数据"}]
        return [
            {"label": "Stars", "value": f"{int(float(row.get('stars', 0) or 0)):,}", "hint": "关注度"},
            {"label": "Forks", "value": f"{int(float(row.get('forks', 0) or 0)):,}", "hint": "复用规模"},
            {"label": "Watchers", "value": f"{int(float(row.get('watchers', 0) or 0)):,}", "hint": "订阅者"},
            {"label": "Open Issues", "value": f"{int(float(row.get('open_issues', 0) or 0)):,}", "hint": "待处理问题"},
            {"label": "贡献者", "value": f"{int(float(row.get('contributors', 0) or 0)):,}", "hint": "采样贡献者"},
            {"label": "近期提交", "value": f"{int(float(row.get('commits_recent', 0) or 0)):,}", "hint": "近 90 天"},
            {"label": "近期 Issue", "value": f"{int(float(row.get('issues_recent', 0) or 0)):,}", "hint": "近 90 天"},
            {"label": "近期 PR", "value": f"{int(float(row.get('prs_recent', 0) or 0)):,}", "hint": "近 90 天"},
            {"label": "Issue 关闭率", "value": f"{float(row.get('issue_close_rate', 0) or 0):.1%}", "hint": "维护响应"},
            {"label": "PR 合并率", "value": f"{float(row.get('pr_merge_rate', 0) or 0):.1%}", "hint": "协作接纳"},
            {"label": "热度评分", "value": f"{float(row.get('popularity_score', 0) or 0):.1%}", "hint": "综合热度"},
            {"label": "国际化评分", "value": f"{float(row.get('globalization_score', 0) or 0):.1%}", "hint": "地域多样性"},
        ]

    @rx.var(cache=True)
    def compare_rows(self) -> list[dict]:
        _ = (self.data_fingerprint, "|".join(self.selected_repos))
        rows = []
        for repo in self.selected_repos:
            index = self._score_index_by_repo.get(repo)
            if index is not None and index < len(self._scores):
                rows.append(self._scores[index])
        return rows

    @rx.var(cache=True)
    def filtered_geo_rows(self) -> list[dict]:
        _ = (self.data_fingerprint, self.selected_geo_repo, self.selected_country)
        if self.selected_geo_repo and self.selected_geo_repo != "全部项目":
            rows = _indexed_rows(self._geo_rows, self._geo_index_by_repo, self.selected_geo_repo)
            if self.selected_country != "全部国家":
                rows = [row for row in rows if row.get("country") == self.selected_country]
            return rows
        if self.selected_country != "全部国家":
            return _indexed_rows(self._geo_rows, self._geo_index_by_country, self.selected_country, limit=2000)
        return self._geo_rows

    @rx.var(cache=True)
    def selected_issue_rows(self) -> list[dict]:
        _ = (self.data_fingerprint, self.selected_repo)
        if not self.selected_repo or self.selected_repo == "全部项目":
            return self._issue_rows[:800]
        return _indexed_rows(self._issue_rows, self._issue_index_by_repo, self.selected_repo)

    @rx.var(cache=True)
    def selected_pull_rows(self) -> list[dict]:
        _ = (self.data_fingerprint, self.selected_repo)
        if not self.selected_repo or self.selected_repo == "全部项目":
            return self._pull_rows[:800]
        return _indexed_rows(self._pull_rows, self._pull_index_by_repo, self.selected_repo)

    @rx.var(cache=True)
    def selected_project_geo_rows(self) -> list[dict]:
        _ = (self.data_fingerprint, self.selected_repo)
        if not self.selected_repo or self.selected_repo == "全部项目":
            return self._geo_rows[:800]
        return _indexed_rows(self._geo_rows, self._geo_index_by_repo, self.selected_repo)

    @rx.var(cache=True)
    def globalization_rank_rows(self) -> list[dict]:
        _ = self.data_fingerprint
        return sorted(self._scores, key=lambda row: float(row.get("globalization_score", 0) or 0), reverse=True)

    @rx.var(cache=True)
    def model_metrics_rows(self) -> list[dict]:
        _ = self.data_fingerprint
        if self._model_metrics_rows:
            return self._model_metrics_rows
        if not self._ml_rows:
            return []
        df = pd.DataFrame(self._ml_rows)
        cluster_count = int(df["cluster"].nunique()) if "cluster" in df.columns else 0
        anomaly_count = int((df.get("anomaly_label", pd.Series(dtype=str)) == "anomaly").sum())
        total = len(df)
        return [
            {"metric": "样本项目数", "value": total, "description": "当前 ml_results.csv 中的项目数量。"},
            {"metric": "K-Means 聚类数", "value": cluster_count, "description": "由离线训练结果读取；完整 inertia 和 silhouette 需重新运行 scripts/train_models.py。"},
            {"metric": "异常项目数", "value": anomaly_count, "description": "Isolation Forest 标记为 anomaly 的项目数量。"},
            {"metric": "异常项目占比", "value": round(anomaly_count / total, 6) if total else 0, "description": "异常项目数量占比。"},
            {"metric": "PCA 解释率", "value": "待生成", "description": "请重新运行 scripts/train_models.py 生成 model_metrics.csv。"},
        ]

    @rx.var(cache=True)
    def cluster_profile_rows(self) -> list[dict]:
        _ = self.data_fingerprint
        if self._cluster_profile_rows:
            return self._cluster_profile_rows
        if not self._ml_rows:
            return []
        df = pd.DataFrame(self._ml_rows)
        if "cluster" not in df.columns:
            return []
        rows = []
        for cluster, group in df.groupby("cluster"):
            avg = group[["popularity_score", "activity_score", "health_score", "globalization_score", "stars", "forks", "contributors"]].apply(pd.to_numeric, errors="coerce").fillna(0).mean()
            representative = group.sort_values(["popularity_score", "activity_score", "health_score"], ascending=False).iloc[0]
            popularity = float(avg.get("popularity_score", 0))
            activity = float(avg.get("activity_score", 0))
            health = float(avg.get("health_score", 0))
            globalization = float(avg.get("globalization_score", 0))
            if popularity >= 0.65 and activity >= 0.55 and health >= 0.55:
                label = "头部活跃型"
            elif popularity >= 0.65 and activity < 0.45:
                label = "高热度维护压力型"
            elif activity >= 0.55 and popularity < 0.55:
                label = "潜力成长型"
            elif health < 0.35:
                label = "健康风险型"
            elif globalization >= 0.55:
                label = "国际化社区型"
            else:
                label = "均衡观察型"
            rows.append(
                {
                    "cluster": cluster,
                    "project_count": int(len(group)),
                    "cluster_label": label,
                    "representative_repo": representative.get("repo", ""),
                    "avg_popularity_score": round(popularity, 6),
                    "avg_activity_score": round(activity, 6),
                    "avg_health_score": round(health, 6),
                    "avg_globalization_score": round(globalization, 6),
                    "description": f"{label}，代表项目为 {representative.get('repo', '')}。",
                }
            )
        return sorted(rows, key=lambda row: int(float(row.get("cluster", 0) or 0)))

    @rx.var(cache=True)
    def trend_summary_rows(self) -> list[dict]:
        _ = (self.data_fingerprint, self.selected_trend_metric, "|".join(self.selected_trend_repos))
        if not self._star_history_rows:
            return []
        metric_map = {"Stars": "stars", "Forks": "forks", "Open Issues": "open_issues"}
        metric = metric_map.get(self.selected_trend_metric, "stars")
        rows = []
        df = pd.DataFrame(self._star_history_rows)
        if not {"repo", "collected_at", metric}.issubset(df.columns):
            return []
        df["collected_at"] = pd.to_datetime(df["collected_at"], errors="coerce", utc=True)
        df[metric] = pd.to_numeric(df[metric], errors="coerce").fillna(0)
        df = df.dropna(subset=["collected_at"]).sort_values(["repo", "collected_at"])
        selected = [repo for repo in self.selected_trend_repos if repo]
        if selected:
            df = df[df["repo"].isin(selected)]
        for repo, group in df.groupby("repo"):
            first = group.iloc[0]
            latest = group.iloc[-1]
            change = int(float(latest[metric]) - float(first[metric]))
            if change == 0:
                continue
            rows.append(
                {
                    "repo": repo,
                    "snapshot_count": int(len(group)),
                    "first_value": int(float(first[metric])),
                    "latest_value": int(float(latest[metric])),
                    "change": change,
                    "first_collected_at": str(first["collected_at"]),
                    "latest_collected_at": str(latest["collected_at"]),
                }
            )
        return sorted(rows, key=lambda row: (row["change"], row["latest_value"]), reverse=True)[:80]

    @rx.var(cache=True)
    def dashboard_chart_key(self) -> str:
        return f"dashboard-{self.selected_language}-{self.search_keyword}-{self.star_min}-{self.star_max}-{self.health_min}-{self.activity_min}-{self.data_fingerprint}"

    @rx.var(cache=True)
    def project_chart_key(self) -> str:
        return f"project-{self.selected_repo}-{self.data_fingerprint}"

    @rx.var(cache=True)
    def compare_chart_key(self) -> str:
        return f"compare-{'|'.join(self.selected_repos)}-{self.compare_candidate_repo}-{self.data_fingerprint}"

    @rx.var(cache=True)
    def geo_chart_key(self) -> str:
        return f"geo-{self.selected_geo_repo}-{self.selected_country}-{self.data_fingerprint}"

    @rx.var(cache=True)
    def ml_chart_key(self) -> str:
        return f"ml-{self.data_fingerprint}"

    @rx.var(cache=True)
    def statistics_metric_chart_key(self) -> str:
        return f"statistics-metric-{self.selected_language}-{self.search_keyword}-{self.selected_distribution_metric}-{self.star_min}-{self.star_max}-{self.health_min}-{self.activity_min}-{self.data_fingerprint}"

    @rx.var(cache=True)
    def statistics_score_chart_key(self) -> str:
        return f"statistics-score-{self.selected_language}-{self.search_keyword}-{self.star_min}-{self.star_max}-{self.health_min}-{self.activity_min}-{self.data_fingerprint}"

    @rx.var(cache=True)
    def statistics_language_score_base_key(self) -> str:
        return f"statistics-language-{self.selected_language}-{self.search_keyword}-{self.star_min}-{self.star_max}-{self.health_min}-{self.activity_min}-{self.data_fingerprint}"

    @rx.var(cache=True)
    def statistics_language_popularity_chart_key(self) -> str:
        return f"{self.statistics_language_score_base_key}-popularity"

    @rx.var(cache=True)
    def statistics_language_activity_chart_key(self) -> str:
        return f"{self.statistics_language_score_base_key}-activity"

    @rx.var(cache=True)
    def statistics_language_health_chart_key(self) -> str:
        return f"{self.statistics_language_score_base_key}-health"

    @rx.var(cache=True)
    def statistics_language_globalization_chart_key(self) -> str:
        return f"{self.statistics_language_score_base_key}-globalization"

    @rx.var(cache=True)
    def statistics_correlation_chart_key(self) -> str:
        return f"statistics-correlation-{self.selected_language}-{self.search_keyword}-{self.star_min}-{self.star_max}-{self.health_min}-{self.activity_min}-{self.data_fingerprint}"

    @rx.var(cache=True)
    def trend_base_chart_key(self) -> str:
        return f"trends-{'|'.join(self.selected_trend_repos)}-{self.data_fingerprint}"

    @rx.var(cache=True)
    def trend_stars_line_chart_key(self) -> str:
        return f"{self.trend_base_chart_key}-stars-line"

    @rx.var(cache=True)
    def trend_forks_line_chart_key(self) -> str:
        return f"{self.trend_base_chart_key}-forks-line"

    @rx.var(cache=True)
    def trend_issues_line_chart_key(self) -> str:
        return f"{self.trend_base_chart_key}-issues-line"

    @rx.var(cache=True)
    def trend_stars_change_chart_key(self) -> str:
        return f"{self.trend_base_chart_key}-stars-change"

    @rx.var(cache=True)
    def trend_forks_change_chart_key(self) -> str:
        return f"{self.trend_base_chart_key}-forks-change"

    @rx.var(cache=True)
    def trend_issues_change_chart_key(self) -> str:
        return f"{self.trend_base_chart_key}-issues-change"

    @rx.var(cache=True)
    def trend_coverage_chart_key(self) -> str:
        return f"trends-coverage-{self.data_fingerprint}"

    @rx.var(cache=True)
    def text_chart_key(self) -> str:
        return f"text-{self.data_fingerprint}"

    @rx.var(cache=True)
    def growth_chart_key(self) -> str:
        return f"growth-{self.data_fingerprint}-{self.star_growth_version}"

    @rx.var(cache=True)
    def star_bar_chart(self) -> go.Figure:
        key = _dashboard_chart_key("star_bar", self.data_fingerprint, self.selected_language, self.search_keyword, self.star_min, self.star_max, self.health_min, self.activity_min)
        return _cached_chart(key, lambda: _build_dashboard_chart("star_bar", self.filtered_scores))

    @rx.var(cache=True)
    def first_year_star_chart(self) -> go.Figure:
        key = _dashboard_chart_key("first_year_star", self.data_fingerprint, self.selected_language, self.search_keyword, self.star_min, self.star_max, self.health_min, self.activity_min)
        return _cached_chart(key, lambda: _build_dashboard_chart("first_year_star", self.filtered_scores))

    @rx.var(cache=True)
    def fork_bar_chart(self) -> go.Figure:
        key = _dashboard_chart_key("fork_bar", self.data_fingerprint, self.selected_language, self.search_keyword, self.star_min, self.star_max, self.health_min, self.activity_min)
        return _cached_chart(key, lambda: _build_dashboard_chart("fork_bar", self.filtered_scores))

    @rx.var(cache=True)
    def star_fork_chart(self) -> go.Figure:
        key = _dashboard_chart_key("star_fork", self.data_fingerprint, self.selected_language, self.search_keyword, self.star_min, self.star_max, self.health_min, self.activity_min)
        return _cached_chart(key, lambda: _build_dashboard_chart("star_fork", self.filtered_scores))

    @rx.var(cache=True)
    def language_chart(self) -> go.Figure:
        key = _dashboard_chart_key("language", self.data_fingerprint, self.selected_language, self.search_keyword, self.star_min, self.star_max, self.health_min, self.activity_min)
        return _cached_chart(key, lambda: _build_dashboard_chart("language", self.filtered_scores))

    @rx.var(cache=True)
    def created_year_chart(self) -> go.Figure:
        key = _dashboard_chart_key("created_year", self.data_fingerprint, self.selected_language, self.search_keyword, self.star_min, self.star_max, self.health_min, self.activity_min)
        return _cached_chart(key, lambda: _build_dashboard_chart("created_year", self.filtered_scores))

    @rx.var(cache=True)
    def quadrant_chart(self) -> go.Figure:
        key = _dashboard_chart_key("quadrant", self.data_fingerprint, self.selected_language, self.search_keyword, self.star_min, self.star_max, self.health_min, self.activity_min)
        return _cached_chart(key, lambda: _build_dashboard_chart("quadrant", self.filtered_scores))

    @rx.var(cache=True)
    def ecosystem_bubble_chart(self) -> go.Figure:
        key = _dashboard_chart_key("ecosystem", self.data_fingerprint, self.selected_language, self.search_keyword, self.star_min, self.star_max, self.health_min, self.activity_min)
        return _cached_chart(key, lambda: _build_dashboard_chart("ecosystem", self.filtered_scores))

    @rx.var(cache=True)
    def dashboard_ecosystem_language_all_chart(self) -> go.Figure:
        return self._dashboard_quick_language_chart(0, "ecosystem")

    @rx.var(cache=True)
    def dashboard_ecosystem_language_1_chart(self) -> go.Figure:
        return self._dashboard_quick_language_chart(1, "ecosystem")

    @rx.var(cache=True)
    def dashboard_ecosystem_language_2_chart(self) -> go.Figure:
        return self._dashboard_quick_language_chart(2, "ecosystem")

    @rx.var(cache=True)
    def dashboard_ecosystem_language_3_chart(self) -> go.Figure:
        return self._dashboard_quick_language_chart(3, "ecosystem")

    @rx.var(cache=True)
    def dashboard_ecosystem_language_all_key(self) -> str:
        return self._dashboard_quick_language_key(0, "ecosystem")

    @rx.var(cache=True)
    def dashboard_ecosystem_language_1_key(self) -> str:
        return self._dashboard_quick_language_key(1, "ecosystem")

    @rx.var(cache=True)
    def dashboard_ecosystem_language_2_key(self) -> str:
        return self._dashboard_quick_language_key(2, "ecosystem")

    @rx.var(cache=True)
    def dashboard_ecosystem_language_3_key(self) -> str:
        return self._dashboard_quick_language_key(3, "ecosystem")

    @rx.var(cache=True)
    def language_treemap_chart(self) -> go.Figure:
        key = _dashboard_chart_key("language_treemap", self.data_fingerprint, self.selected_language, self.search_keyword, self.star_min, self.star_max, self.health_min, self.activity_min)
        return _cached_chart(key, lambda: _build_dashboard_chart("language_treemap", self.filtered_scores))

    @rx.var(cache=True)
    def score_heatmap_chart(self) -> go.Figure:
        key = _dashboard_chart_key("score_heatmap", self.data_fingerprint, self.selected_language, self.search_keyword, self.star_min, self.star_max, self.health_min, self.activity_min)
        return _cached_chart(key, lambda: _build_dashboard_chart("score_heatmap", self.filtered_scores))

    @rx.var(cache=True)
    def metric_distribution_chart(self) -> go.Figure:
        key = _statistics_chart_key("metric_distribution", self.data_fingerprint, self.selected_language, self.search_keyword, self.star_min, self.star_max, self.health_min, self.activity_min, self.selected_distribution_metric)
        return _cached_chart(key, lambda: _build_statistics_chart("metric_distribution", self.filtered_scores, self.selected_distribution_metric))

    @rx.var(cache=True)
    def score_distribution_chart(self) -> go.Figure:
        key = _statistics_chart_key("score_distribution", self.data_fingerprint, self.selected_language, self.search_keyword, self.star_min, self.star_max, self.health_min, self.activity_min)
        return _cached_chart(key, lambda: _build_statistics_chart("score_distribution", self.filtered_scores))

    @rx.var(cache=True)
    def language_popularity_score_box_chart(self) -> go.Figure:
        key = _statistics_chart_key("language_score", self.data_fingerprint, self.selected_language, self.search_keyword, self.star_min, self.star_max, self.health_min, self.activity_min, "热度评分")
        return _cached_chart(key, lambda: _build_statistics_chart("language_score", self.filtered_scores, "热度评分"))

    @rx.var(cache=True)
    def language_activity_score_box_chart(self) -> go.Figure:
        key = _statistics_chart_key("language_score", self.data_fingerprint, self.selected_language, self.search_keyword, self.star_min, self.star_max, self.health_min, self.activity_min, "活跃度评分")
        return _cached_chart(key, lambda: _build_statistics_chart("language_score", self.filtered_scores, "活跃度评分"))

    @rx.var(cache=True)
    def language_health_score_box_chart(self) -> go.Figure:
        key = _statistics_chart_key("language_score", self.data_fingerprint, self.selected_language, self.search_keyword, self.star_min, self.star_max, self.health_min, self.activity_min, "健康度评分")
        return _cached_chart(key, lambda: _build_statistics_chart("language_score", self.filtered_scores, "健康度评分"))

    @rx.var(cache=True)
    def language_globalization_score_box_chart(self) -> go.Figure:
        key = _statistics_chart_key("language_score", self.data_fingerprint, self.selected_language, self.search_keyword, self.star_min, self.star_max, self.health_min, self.activity_min, "国际化评分")
        return _cached_chart(key, lambda: _build_statistics_chart("language_score", self.filtered_scores, "国际化评分"))

    @rx.var(cache=True)
    def correlation_heatmap_chart(self) -> go.Figure:
        key = _statistics_chart_key("correlation", self.data_fingerprint, self.selected_language, self.search_keyword, self.star_min, self.star_max, self.health_min, self.activity_min)
        return _cached_chart(key, lambda: _build_statistics_chart("correlation", self.filtered_scores))

    @rx.var(cache=True)
    def selected_project_radar_chart(self) -> go.Figure:
        key = f"project-radar:{self.data_fingerprint}:{self.selected_repo}"
        return _cached_chart(key, lambda: make_project_radar(self.selected_project_row))

    @rx.var(cache=True)
    def selected_project_activity_chart(self) -> go.Figure:
        key = f"project-activity:{self.data_fingerprint}:{self.selected_repo}"
        return _cached_chart(key, lambda: make_recent_activity_bar(self.selected_project_row))

    @rx.var(cache=True)
    def selected_issue_status_chart(self) -> go.Figure:
        key = f"project-issue-status:{self.data_fingerprint}:{self.selected_repo}"
        return _cached_chart(key, lambda: make_issue_status_chart(pd.DataFrame(self.selected_issue_rows)))

    @rx.var(cache=True)
    def selected_pull_status_chart(self) -> go.Figure:
        key = f"project-pull-status:{self.data_fingerprint}:{self.selected_repo}"
        return _cached_chart(key, lambda: make_pull_status_chart(pd.DataFrame(self.selected_pull_rows)))

    @rx.var(cache=True)
    def selected_issue_topic_chart(self) -> go.Figure:
        key = f"project-issue-topic:{self.data_fingerprint}:{self.selected_repo}"
        return _cached_chart(key, lambda: make_issue_topic_bar(pd.DataFrame(self.selected_issue_rows)))

    @rx.var(cache=True)
    def issue_topic_chart(self) -> go.Figure:
        _ = self.data_fingerprint
        return make_issue_topic_bar(pd.DataFrame(self._issue_rows))

    @rx.var(cache=True)
    def selected_country_chart(self) -> go.Figure:
        key = f"project-country:{self.data_fingerprint}:{self.selected_repo}"
        return _cached_chart(key, lambda: make_country_top_bar(pd.DataFrame(self.selected_project_geo_rows)))

    @rx.var(cache=True)
    def compare_bar_chart(self) -> go.Figure:
        return make_score_compare_bar(pd.DataFrame(self.compare_rows))

    @rx.var(cache=True)
    def compare_radar_chart(self) -> go.Figure:
        return make_multi_project_radar(pd.DataFrame(self.compare_rows))

    @rx.var(cache=True)
    def compare_rate_chart(self) -> go.Figure:
        return make_rate_compare_bar(pd.DataFrame(self.compare_rows))

    @rx.var(cache=True)
    def world_map_chart(self) -> go.Figure:
        key = _geo_chart_key("world", self.data_fingerprint, self.selected_geo_repo, self.selected_country)
        return _cached_chart(key, lambda: _build_geo_chart("world", self.filtered_geo_rows))

    @rx.var(cache=True)
    def geo_world_country_all_chart(self) -> go.Figure:
        return self._geo_quick_country_chart(0, "world")

    @rx.var(cache=True)
    def geo_world_country_1_chart(self) -> go.Figure:
        return self._geo_quick_country_chart(1, "world")

    @rx.var(cache=True)
    def geo_world_country_2_chart(self) -> go.Figure:
        return self._geo_quick_country_chart(2, "world")

    @rx.var(cache=True)
    def geo_world_country_3_chart(self) -> go.Figure:
        return self._geo_quick_country_chart(3, "world")

    @rx.var(cache=True)
    def geo_world_country_all_key(self) -> str:
        return self._geo_quick_country_key(0, "world")

    @rx.var(cache=True)
    def geo_world_country_1_key(self) -> str:
        return self._geo_quick_country_key(1, "world")

    @rx.var(cache=True)
    def geo_world_country_2_key(self) -> str:
        return self._geo_quick_country_key(2, "world")

    @rx.var(cache=True)
    def geo_world_country_3_key(self) -> str:
        return self._geo_quick_country_key(3, "world")

    @rx.var(cache=True)
    def geo_world_language_all_chart(self) -> go.Figure:
        return self._geo_quick_language_chart(0, "world")

    @rx.var(cache=True)
    def geo_world_language_1_chart(self) -> go.Figure:
        return self._geo_quick_language_chart(1, "world")

    @rx.var(cache=True)
    def geo_world_language_2_chart(self) -> go.Figure:
        return self._geo_quick_language_chart(2, "world")

    @rx.var(cache=True)
    def geo_world_language_3_chart(self) -> go.Figure:
        return self._geo_quick_language_chart(3, "world")

    @rx.var(cache=True)
    def geo_world_language_all_key(self) -> str:
        return self._geo_quick_language_key(0, "world")

    @rx.var(cache=True)
    def geo_world_language_1_key(self) -> str:
        return self._geo_quick_language_key(1, "world")

    @rx.var(cache=True)
    def geo_world_language_2_key(self) -> str:
        return self._geo_quick_language_key(2, "world")

    @rx.var(cache=True)
    def geo_world_language_3_key(self) -> str:
        return self._geo_quick_language_key(3, "world")

    @rx.var(cache=True)
    def dashboard_world_map_chart(self) -> go.Figure:
        _ = self.data_fingerprint
        return make_world_map(pd.DataFrame(self._geo_rows))

    @rx.var(cache=True)
    def city_bubble_chart(self) -> go.Figure:
        key = _geo_chart_key("city_bubble", self.data_fingerprint, self.selected_geo_repo, self.selected_country)
        return _cached_chart(key, lambda: _build_geo_chart("city_bubble", self.filtered_geo_rows))

    @rx.var(cache=True)
    def dashboard_city_bubble_chart(self) -> go.Figure:
        _ = self.data_fingerprint
        return make_city_bubble_map(pd.DataFrame(self._geo_rows))

    @rx.var(cache=True)
    def country_top_chart(self) -> go.Figure:
        key = _geo_chart_key("country_top", self.data_fingerprint, self.selected_geo_repo, self.selected_country)
        return _cached_chart(key, lambda: _build_geo_chart("country_top", self.filtered_geo_rows))

    @rx.var(cache=True)
    def dashboard_country_top_chart(self) -> go.Figure:
        _ = self.data_fingerprint
        return make_country_top_bar(pd.DataFrame(self._geo_rows))

    @rx.var(cache=True)
    def city_top_chart(self) -> go.Figure:
        key = _geo_chart_key("city_top", self.data_fingerprint, self.selected_geo_repo, self.selected_country)
        return _cached_chart(key, lambda: _build_geo_chart("city_top", self.filtered_geo_rows))

    @rx.var(cache=True)
    def dashboard_city_top_chart(self) -> go.Figure:
        _ = self.data_fingerprint
        return make_city_top_bar(pd.DataFrame(self._geo_rows))

    @rx.var(cache=True)
    def project_country_heatmap_chart(self) -> go.Figure:
        key = _geo_chart_key("project_country", self.data_fingerprint, self.selected_geo_repo, self.selected_country)
        return _cached_chart(key, lambda: _build_geo_chart("project_country", self.filtered_geo_rows))

    @rx.var(cache=True)
    def dashboard_project_country_heatmap_chart(self) -> go.Figure:
        _ = self.data_fingerprint
        return make_project_country_heatmap(pd.DataFrame(self._geo_rows))

    @rx.var(cache=True)
    def cluster_scatter_chart(self) -> go.Figure:
        _ = self.data_fingerprint
        return make_cluster_scatter(pd.DataFrame(self._ml_rows))

    @rx.var(cache=True)
    def cluster_average_chart(self) -> go.Figure:
        _ = self.data_fingerprint
        return make_cluster_average_heatmap(pd.DataFrame(self._ml_rows))

    @rx.var(cache=True)
    def cluster_radar_chart(self) -> go.Figure:
        _ = self.data_fingerprint
        return make_cluster_radar(pd.DataFrame(self._ml_rows))

    @rx.var(cache=True)
    def cluster_profile_chart(self) -> go.Figure:
        _ = self.data_fingerprint
        return make_cluster_profile_bar(pd.DataFrame(self.cluster_profile_rows))

    @rx.var(cache=True)
    def anomaly_scatter_chart(self) -> go.Figure:
        _ = self.data_fingerprint
        return make_anomaly_scatter(pd.DataFrame(self._ml_rows))

    @rx.var(cache=True)
    def risk_project_chart(self) -> go.Figure:
        _ = self.data_fingerprint
        return make_risk_project_bar(pd.DataFrame(self._ml_rows))

    @rx.var(cache=True)
    def text_embedding_chart(self) -> go.Figure:
        _ = self.data_fingerprint
        return make_text_embedding_scatter(pd.DataFrame(self._text_rows))

    @rx.var(cache=True)
    def text_similarity_chart(self) -> go.Figure:
        _ = self.data_fingerprint
        return make_similarity_heatmap(pd.DataFrame(self._text_rows), pd.DataFrame(self._text_similarity_rows))

    @rx.var(cache=True)
    def commit_type_chart(self) -> go.Figure:
        _ = self.data_fingerprint
        return make_commit_type_bar(pd.DataFrame(self._text_rows))

    @rx.var(cache=True)
    def trend_stars_line_chart(self) -> go.Figure:
        _ = self.data_fingerprint
        return make_time_series_line(pd.DataFrame(self._star_history_rows), self.selected_trend_repos, "Stars")

    @rx.var(cache=True)
    def trend_forks_line_chart(self) -> go.Figure:
        _ = self.data_fingerprint
        return make_time_series_line(pd.DataFrame(self._star_history_rows), self.selected_trend_repos, "Forks")

    @rx.var(cache=True)
    def trend_issues_line_chart(self) -> go.Figure:
        _ = self.data_fingerprint
        return make_time_series_line(pd.DataFrame(self._star_history_rows), self.selected_trend_repos, "Open Issues")

    @rx.var(cache=True)
    def trend_stars_change_chart(self) -> go.Figure:
        _ = self.data_fingerprint
        return make_time_series_change_bar(pd.DataFrame(self._star_history_rows), self.selected_trend_repos, "Stars")

    @rx.var(cache=True)
    def trend_forks_change_chart(self) -> go.Figure:
        _ = self.data_fingerprint
        return make_time_series_change_bar(pd.DataFrame(self._star_history_rows), self.selected_trend_repos, "Forks")

    @rx.var(cache=True)
    def trend_issues_change_chart(self) -> go.Figure:
        _ = self.data_fingerprint
        return make_time_series_change_bar(pd.DataFrame(self._star_history_rows), self.selected_trend_repos, "Open Issues")

    @rx.var(cache=True)
    def snapshot_coverage_chart(self) -> go.Figure:
        _ = self.data_fingerprint
        return make_snapshot_coverage_bar(pd.DataFrame(self._star_history_rows))

    @rx.var(cache=True)
    def star_growth_30m_rows(self) -> list[dict]:
        _ = (self.data_fingerprint, self.star_growth_version)
        return sorted(self._star_growth_rows, key=lambda row: float(row.get("growth_30m", 0) or 0), reverse=True)[:50]

    @rx.var(cache=True)
    def star_growth_24h_rows(self) -> list[dict]:
        _ = (self.data_fingerprint, self.star_growth_version)
        return sorted(self._star_growth_rows, key=lambda row: float(row.get("growth_24h", 0) or 0), reverse=True)[:50]

    @rx.var(cache=True)
    def star_growth_status(self) -> str:
        _ = (self.data_fingerprint, self.star_growth_version)
        if not self._star_growth_rows:
            return "暂无 Star 增长数据。请先运行 GitHub 采集流水线，再运行 scripts/build_star_growth.py 生成 star_growth.csv。"
        def is_true(value) -> bool:
            return str(value).lower() in {"true", "1", "yes"}
        growth_30m = [float(row.get("growth_30m", 0) or 0) for row in self._star_growth_rows]
        growth_24h = [float(row.get("growth_24h", 0) or 0) for row in self._star_growth_rows]
        max_30m = max(growth_30m) if growth_30m else 0
        max_24h = max(growth_24h) if growth_24h else 0
        has_30m_window = any(is_true(row.get("window_30m_available")) for row in self._star_growth_rows)
        has_24h_window = any(is_true(row.get("window_24h_available")) for row in self._star_growth_rows)
        if max_30m > 0 and not has_24h_window:
            return "30 分钟 Stars 增长已可用；当前缺少完整 24 小时前快照，24 小时图仅用于参考现有历史快照跨度内的变化。"
        if max_30m <= 0 and max_24h <= 0:
            return "当前 30 分钟和 24 小时增长都为 0：通常是因为 star_history.csv 只有一次采集快照，或采样窗口内 Stars 没有变化。请间隔 30 分钟或 24 小时重复采集后重新生成增长榜。"
        if max_30m <= 0 or not has_30m_window:
            return "24 小时增长榜已有变化；30 分钟窗口暂未观测到新增 Stars。"
        if max_24h <= 0 or not has_24h_window:
            return "30 分钟增长榜已有变化；24 小时窗口暂未观测到新增 Stars。"
        return "Star 增长榜已加载，数据来自离线采集快照，不会在页面渲染时请求 GitHub。"

    @rx.var(cache=True)
    def star_growth_30m_chart(self) -> go.Figure:
        _ = (self.data_fingerprint, self.star_growth_version)
        return make_star_growth_bar(pd.DataFrame(self._star_growth_rows), "30m")

    @rx.var(cache=True)
    def star_growth_24h_chart(self) -> go.Figure:
        _ = (self.data_fingerprint, self.star_growth_version)
        return make_star_growth_bar(pd.DataFrame(self._star_growth_rows), "24h")

    @rx.var(cache=True)
    def trending_rows(self) -> list[dict]:
        _ = self.trending_version
        return self._trending_rows

    @rx.var(cache=True)
    def trending_star_chart(self) -> go.Figure:
        _ = self.trending_version
        return make_trending_star_bar(pd.DataFrame(self._trending_rows))

    @rx.var(cache=True)
    def trending_language_chart(self) -> go.Figure:
        _ = self.trending_version
        return make_trending_language_bar(pd.DataFrame(self._trending_rows))

    @rx.var(cache=True)
    def trending_repo_count(self) -> str:
        _ = self.trending_version
        return str(len(self._trending_rows))

    @rx.var(cache=True)
    def trending_total_stars(self) -> str:
        _ = self.trending_version
        total = sum(float(row.get("stars", 0) or 0) for row in self._trending_rows)
        return f"{total:,.0f}"

    @rx.var(cache=True)
    def trending_total_forks(self) -> str:
        _ = self.trending_version
        total = sum(float(row.get("forks", 0) or 0) for row in self._trending_rows)
        return f"{total:,.0f}"

    @rx.var(cache=True)
    def star_rank_rows(self) -> list[dict]:
        _ = self.star_rank_version
        return self._star_rank_rows

    @rx.var(cache=True)
    def star_rank_chart(self) -> go.Figure:
        _ = self.star_rank_version
        return make_star_rank_bar(pd.DataFrame(self._star_rank_rows))

    @rx.var(cache=True)
    def star_rank_language_chart(self) -> go.Figure:
        _ = self.star_rank_version
        return make_star_rank_language_bar(pd.DataFrame(self._star_rank_rows))

    @rx.var(cache=True)
    def star_rank_repo_count(self) -> str:
        _ = self.star_rank_version
        return str(len(self._star_rank_rows))

    @rx.var(cache=True)
    def star_rank_total_stars(self) -> str:
        _ = self.star_rank_version
        total = sum(float(row.get("stars", 0) or 0) for row in self._star_rank_rows)
        return f"{total:,.0f}"

    @rx.var(cache=True)
    def star_rank_total_forks(self) -> str:
        _ = self.star_rank_version
        total = sum(float(row.get("forks", 0) or 0) for row in self._star_rank_rows)
        return f"{total:,.0f}"

    def refresh_star_rank_projects(self):
        try:
            limit = max(1, min(100, int(float(self.star_rank_limit or 30))))
        except Exception:
            limit = 30
        self.star_rank_running = True
        self.star_rank_progress = 0
        self.star_rank_status = "正在查询 GitHub Stars 实时榜..."
        yield
        try:
            rows, search_query = fetch_star_rank_projects(self.star_rank_query, self.star_rank_language, limit)
        except Exception as exc:
            self.star_rank_status = f"GitHub Stars 实时榜查询失败：{exc}"
            self.star_rank_running = False
            yield
            return
        if not rows:
            self.star_rank_status = "GitHub 没有返回仓库，请放宽查询条件后重试。"
            self.star_rank_progress = 0
            self.star_rank_running = False
            yield
            return
        self._star_rank_rows = rows
        self.star_rank_version = datetime.now().strftime("%Y%m%d%H%M%S")
        self.star_rank_progress = 100
        self.star_rank_running = False
        self.star_rank_status = f"已实时查询 {len(rows)} 个仓库。查询条件：{search_query}"
        yield

    def refresh_trending_projects(self):
        try:
            limit = max(1, min(100, int(float(self.realtime_repo_limit or 10))))
        except Exception:
            limit = 10
        self.realtime_growth_total = 0
        self.realtime_growth_done = 0
        self.realtime_growth_progress = 0
        self.realtime_growth_running = True
        self.realtime_growth_status = "正在采集 GitHub Trending 仓库..."
        yield
        try:
            rows, trending_source = fetch_trending_projects(
                self.realtime_trending_language,
                self.realtime_trending_since,
                limit,
            )
        except Exception as exc:
            self.realtime_growth_status = f"GitHub Trending 采集失败：{exc}"
            self.realtime_growth_running = False
            yield
            return
        if not rows:
            self.realtime_growth_status = "GitHub Trending 没有返回仓库，请切换语言或时间范围后重试。"
            self.realtime_growth_progress = 0
            self.realtime_growth_done = 0
            self.realtime_growth_total = 0
            self.realtime_growth_running = False
            yield
            return
        self._trending_rows = rows
        self.trending_version = datetime.now().strftime("%Y%m%d%H%M%S")
        self.realtime_growth_total = len(rows)
        self.realtime_growth_done = len(rows)
        self.realtime_growth_progress = 100
        self.realtime_growth_running = False
        self.realtime_growth_status = f"已实时采集 {len(rows)} 个 {trending_source} 仓库，页面已更新。"
        yield
