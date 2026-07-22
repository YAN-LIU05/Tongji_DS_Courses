from __future__ import annotations

import reflex as rx

from ..components.chart_card import chart_card, plotly_chart
from ..components.layout import app_layout, page_header
from ..components.project_table import project_table
from ..state import LensState


def compare() -> rx.Component:
    return app_layout(
        rx.vstack(
            page_header("项目对比", "选择 2 到 5 个项目，对比核心评分和协作效率。"),
            rx.hstack(
                rx.select(LensState.repo_options, value=LensState.compare_candidate_repo, on_change=LensState.select_compare_repo, placeholder="选择项目"),
                rx.button("加入对比", on_click=LensState.add_compare_repo, variant="soft"),
                rx.button("清空对比", on_click=LensState.clear_compare_repos, variant="soft"),
                width="100%",
                wrap="wrap",
            ),
            rx.hstack(rx.text("当前对比：", color="#6b7280"), rx.foreach(LensState.selected_repos, lambda repo: rx.badge(repo, color_scheme="blue", variant="soft")), wrap="wrap"),
            rx.grid(
                chart_card("评分对比柱状图", plotly_chart(LensState.compare_bar_chart, LensState.compare_chart_key), "对比热度、活跃度、健康度和国际化评分。"),
                chart_card("多项目雷达图", plotly_chart(LensState.compare_radar_chart, LensState.compare_chart_key), "快速识别不同项目优势维度。"),
                columns="2",
                spacing="4",
                width="100%",
            ),
            chart_card("Issue 关闭率 / PR 合并率对比", plotly_chart(LensState.compare_rate_chart, LensState.compare_chart_key), "观察项目协作效率和维护响应差异。"),
            chart_card("对比表格", project_table(LensState.compare_rows), "最多展示 5 个被选项目。"),
            spacing="5",
            align_items="stretch",
        )
    )
