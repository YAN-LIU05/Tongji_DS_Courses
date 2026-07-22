from __future__ import annotations

import reflex as rx

from ..components.chart_card import chart_card, plotly_chart
from ..components.layout import app_layout, page_header
from ..state import LensState


TREND_COLUMNS = [
    {"id": "repo", "name": "项目"},
    {"id": "snapshot_count", "name": "快照数"},
    {"id": "first_value", "name": "首个值"},
    {"id": "latest_value", "name": "最新值"},
    {"id": "change", "name": "变化量"},
    {"id": "first_collected_at", "name": "首个采集时间"},
    {"id": "latest_collected_at", "name": "最新采集时间"},
]


def trend_line_tabs() -> rx.Component:
    return rx.tabs.root(
        rx.tabs.list(
            rx.tabs.trigger("Stars", value="stars"),
            rx.tabs.trigger("Forks", value="forks"),
            rx.tabs.trigger("Open Issues", value="issues"),
            width="100%",
            flex_wrap="wrap",
        ),
        rx.tabs.content(plotly_chart(LensState.trend_stars_line_chart, LensState.trend_stars_line_chart_key), value="stars"),
        rx.tabs.content(plotly_chart(LensState.trend_forks_line_chart, LensState.trend_forks_line_chart_key), value="forks"),
        rx.tabs.content(plotly_chart(LensState.trend_issues_line_chart, LensState.trend_issues_line_chart_key), value="issues"),
        default_value="stars",
        width="100%",
    )


def trend_change_tabs() -> rx.Component:
    return rx.tabs.root(
        rx.tabs.list(
            rx.tabs.trigger("Stars", value="stars"),
            rx.tabs.trigger("Forks", value="forks"),
            rx.tabs.trigger("Open Issues", value="issues"),
            width="100%",
            flex_wrap="wrap",
        ),
        rx.tabs.content(plotly_chart(LensState.trend_stars_change_chart, LensState.trend_stars_change_chart_key), value="stars"),
        rx.tabs.content(plotly_chart(LensState.trend_forks_change_chart, LensState.trend_forks_change_chart_key), value="forks"),
        rx.tabs.content(plotly_chart(LensState.trend_issues_change_chart, LensState.trend_issues_change_chart_key), value="issues"),
        default_value="stars",
        width="100%",
    )


def trends() -> rx.Component:
    return app_layout(
        rx.vstack(
            page_header("时间序列趋势", "基于离线采集的 star_history.csv 观察 Stars、Forks 和 Open Issues 的历史快照变化。"),
            rx.callout(
                "本页只读取 data/processed/star_history.csv；曲线的时间粒度取决于离线采集频率，不会在页面渲染时请求 GitHub。",
                color_scheme="blue",
                width="100%",
            ),
            rx.hstack(
                rx.select(LensState.repo_options, value=LensState.trend_candidate_repo, on_change=LensState.select_trend_repo, placeholder="选择项目"),
                rx.button("加入趋势对比", on_click=LensState.add_trend_repo, variant="soft"),
                rx.button("清空选择", on_click=LensState.clear_trend_repos, variant="soft"),
                width="100%",
                wrap="wrap",
                align_items="center",
            ),
            rx.hstack(
                rx.text("当前趋势对比：", color="#6b7280"),
                rx.foreach(LensState.selected_trend_repos, lambda repo: rx.badge(repo, color_scheme="blue", variant="soft")),
                rx.text("未选择时各指标默认展示累计变化量最高且不为 0 的项目。", color="#6b7280", font_size="13px"),
                wrap="wrap",
            ),
            chart_card("历史快照趋势线", trend_line_tabs(), "Stars、Forks、Open Issues 三张趋势线已预先生成；横轴为第 N 次快照，纵轴为相对首个快照的累计变化量。"),
            rx.grid(
                chart_card("历史快照变化排行", trend_change_tabs(), "Stars、Forks、Open Issues 三张排行已预先生成，并过滤变化量为 0 的项目。"),
                chart_card("采集快照覆盖", plotly_chart(LensState.snapshot_coverage_chart, LensState.trend_coverage_chart_key), "检查哪些项目拥有更多历史快照，辅助判断趋势可信度。"),
                columns="2",
                spacing="4",
                width="100%",
            ),
            chart_card(
                "时间序列摘要表",
                rx.data_table(data=LensState.trend_summary_rows, columns=TREND_COLUMNS, pagination=True, search=True),
                "默认核对 Stars 的首个值、最新值、变化量和采集时间范围。",
            ),
            spacing="5",
            align_items="stretch",
        )
    )
