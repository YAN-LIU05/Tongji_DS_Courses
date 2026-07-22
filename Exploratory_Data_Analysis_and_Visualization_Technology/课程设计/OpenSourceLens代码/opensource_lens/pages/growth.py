from __future__ import annotations

import reflex as rx

from ..components.chart_card import chart_card, plotly_chart
from ..components.layout import app_layout, page_header
from ..components.metric_card import metric_card
from ..state import LensState

TRENDING_COLUMNS = [
    {"id": "rank", "name": "排名"},
    {"id": "repo", "name": "仓库"},
    {"id": "language", "name": "语言"},
    {"id": "stars", "name": "Stars"},
    {"id": "forks", "name": "Forks"},
    {"id": "period_stars", "name": "周期新增 Stars"},
    {"id": "description", "name": "简介"},
    {"id": "url", "name": "URL"},
    {"id": "collected_at", "name": "采集时间"},
    {"id": "source", "name": "来源"},
]

SEARCH_LANGUAGE_OPTIONS = ["全部语言", "Python", "TypeScript", "JavaScript", "Rust", "Go", "Java", "C++", "Jupyter Notebook"]
TRENDING_SINCE_OPTIONS = ["今日", "本周", "本月"]


def growth() -> rx.Component:
    return app_layout(
        rx.vstack(
            page_header("GitHub Trending 实时榜", "实时采集 GitHub Trending，展示当前热门仓库排名、语言、Stars、Forks 和项目简介。"),
            rx.callout(
                "本页只在点击按钮时采集 GitHub Trending 页面；不会读取本地项目列表，不会在页面渲染时自动请求接口，也不会逐仓库调用 stargazers API。",
                color_scheme="blue",
                width="100%",
            ),
            rx.hstack(
                rx.text("Trending 语言", color="#6b7280"),
                rx.select(
                    SEARCH_LANGUAGE_OPTIONS,
                    value=LensState.realtime_trending_language,
                    on_change=LensState.set_realtime_trending_language,
                ),
                rx.text("Trending 时间范围", color="#6b7280"),
                rx.select(
                    TRENDING_SINCE_OPTIONS,
                    value=LensState.realtime_trending_since,
                    on_change=LensState.set_realtime_trending_since,
                ),
                rx.text("Trending 项目数", color="#6b7280"),
                rx.select(["10", "20", "30", "50", "80", "100"], value=LensState.realtime_repo_limit, on_change=LensState.set_realtime_repo_limit),
                rx.button("实时刷新 Trending", on_click=LensState.refresh_trending_projects, disabled=LensState.realtime_growth_running),
                width="100%",
                wrap="wrap",
                align_items="center",
            ),
            rx.vstack(
                rx.hstack(
                    rx.cond(
                        LensState.realtime_growth_running,
                        rx.spinner(size="2"),
                        rx.box(width="18px", height="18px"),
                    ),
                    rx.text(LensState.realtime_growth_status, color="#4b5563", font_size="14px"),
                    rx.spacer(),
                    rx.text(
                        LensState.realtime_growth_done,
                        " / ",
                        LensState.realtime_growth_total,
                        "（",
                        LensState.realtime_growth_progress,
                        "%）",
                        color="#6b7280",
                        font_size="13px",
                    ),
                    width="100%",
                    align_items="center",
                ),
                rx.progress(value=LensState.realtime_growth_progress, width="100%"),
                width="100%",
                spacing="2",
            ),
            rx.grid(
                metric_card("Trending 仓库数", LensState.trending_repo_count, "本次实时采集结果"),
                metric_card("总 Stars", LensState.trending_total_stars, "当前榜单仓库累计"),
                metric_card("总 Forks", LensState.trending_total_forks, "当前榜单仓库累计"),
                columns="3",
                spacing="4",
                width="100%",
            ),
            rx.grid(
                chart_card("Trending Stars 排行", plotly_chart(LensState.trending_star_chart, LensState.trending_version), "按当前 Trending 榜单仓库的 Stars 规模展示。"),
                chart_card("Trending 语言分布", plotly_chart(LensState.trending_language_chart, LensState.trending_version), "观察当前热门项目的主要技术栈。"),
                columns="2",
                spacing="4",
                width="100%",
            ),
            chart_card(
                "GitHub Trending 仓库明细",
                rx.data_table(data=LensState.trending_rows, columns=TRENDING_COLUMNS, pagination=True, search=True),
                "包含排名、仓库名、语言、Stars、Forks、简介、URL 和实时采集时间。",
            ),
            spacing="5",
            align_items="stretch",
        )
    )
