from __future__ import annotations

import reflex as rx

from ..components.chart_card import chart_card, plotly_chart
from ..components.layout import app_layout, page_header
from ..components.metric_card import metric_card
from ..state import LensState

STAR_RANK_COLUMNS = [
    {"id": "rank", "name": "排名"},
    {"id": "repo", "name": "仓库"},
    {"id": "language", "name": "语言"},
    {"id": "stars", "name": "Stars"},
    {"id": "forks", "name": "Forks"},
    {"id": "open_issues", "name": "Open Issues"},
    {"id": "description", "name": "简介"},
    {"id": "url", "name": "URL"},
    {"id": "updated_at", "name": "更新时间"},
    {"id": "pushed_at", "name": "最近 Push"},
    {"id": "collected_at", "name": "查询时间"},
]

STAR_LANGUAGE_OPTIONS = ["全部语言", "Python", "TypeScript", "JavaScript", "Rust", "Go", "Java", "C++", "Jupyter Notebook"]


def stars() -> rx.Component:
    return app_layout(
        rx.vstack(
            page_header("Stars 实时榜", "按钮触发查询 GitHub 当前 Stars 排名，展示仓库、语言、Stars、Forks、简介和 URL。"),
            rx.callout(
                "本页只在点击按钮时调用 GitHub Search API，不读取本地项目列表，也不会在页面渲染时自动请求接口。",
                color_scheme="blue",
                width="100%",
            ),
            rx.hstack(
                rx.input(
                    placeholder="GitHub 查询条件，例如 stars:>1000 topic:machine-learning",
                    value=LensState.star_rank_query,
                    on_change=LensState.set_star_rank_query,
                    width="min(520px, 100%)",
                ),
                rx.text("语言", color="#6b7280"),
                rx.select(STAR_LANGUAGE_OPTIONS, value=LensState.star_rank_language, on_change=LensState.set_star_rank_language),
                rx.text("数量", color="#6b7280"),
                rx.select(["10", "20", "30", "50", "80", "100"], value=LensState.star_rank_limit, on_change=LensState.set_star_rank_limit),
                rx.button("实时查询 Stars 榜", on_click=LensState.refresh_star_rank_projects, disabled=LensState.star_rank_running),
                width="100%",
                wrap="wrap",
                align_items="center",
            ),
            rx.vstack(
                rx.hstack(
                    rx.cond(
                        LensState.star_rank_running,
                        rx.spinner(size="2"),
                        rx.box(width="18px", height="18px"),
                    ),
                    rx.text(LensState.star_rank_status, color="#4b5563", font_size="14px"),
                    rx.spacer(),
                    rx.text(LensState.star_rank_progress, "%", color="#6b7280", font_size="13px"),
                    width="100%",
                    align_items="center",
                ),
                rx.progress(value=LensState.star_rank_progress, width="100%"),
                width="100%",
                spacing="2",
            ),
            rx.grid(
                metric_card("仓库数", LensState.star_rank_repo_count, "本次实时查询结果"),
                metric_card("总 Stars", LensState.star_rank_total_stars, "当前榜单仓库累计"),
                metric_card("总 Forks", LensState.star_rank_total_forks, "当前榜单仓库累计"),
                columns="3",
                spacing="4",
                width="100%",
            ),
            rx.grid(
                chart_card("Stars 排行", plotly_chart(LensState.star_rank_chart, LensState.star_rank_version), "按 GitHub 当前 Stars 数排序。"),
                chart_card("语言分布", plotly_chart(LensState.star_rank_language_chart, LensState.star_rank_version), "观察高 Stars 仓库的主要技术栈。"),
                columns="2",
                spacing="4",
                width="100%",
            ),
            chart_card(
                "Stars 实时榜明细",
                rx.data_table(data=LensState.star_rank_rows, columns=STAR_RANK_COLUMNS, pagination=True, search=True),
                "包含排名、仓库名、语言、Stars、Forks、简介、URL 和实时查询时间。",
            ),
            spacing="5",
            align_items="stretch",
        )
    )
