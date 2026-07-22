from __future__ import annotations

import reflex as rx

from ..components.chart_card import chart_card, plotly_chart
from ..components.layout import app_layout, page_header
from ..components.metric_card import metric_card
from ..state import LensState


def project() -> rx.Component:
    return app_layout(
        rx.vstack(
            page_header("项目详情", "查看单个项目的基础指标和协作状态。"),
            rx.hstack(
                rx.select(LensState.repo_options, value=LensState.selected_repo, on_change=LensState.set_selected_repo, placeholder="选择项目"),
                width="100%",
            ),
            rx.grid(
                rx.foreach(LensState.selected_project_metrics, lambda item: metric_card(item["label"], item["value"], item["hint"])),
                columns="4",
                spacing="4",
                width="100%",
            ),
            rx.grid(
                chart_card("项目雷达图", plotly_chart(LensState.selected_project_radar_chart, LensState.project_chart_key), "展示热度、活跃、健康和国际化评分。"),
                chart_card("近期活动概览", plotly_chart(LensState.selected_project_activity_chart, LensState.project_chart_key), "展示近期提交、Issue 和 PR 规模。"),
                columns="2",
                spacing="4",
                width="100%",
            ),
            rx.grid(
                chart_card("Issue 状态分布", plotly_chart(LensState.selected_issue_status_chart, LensState.project_chart_key), "观察当前项目 Issue 关闭情况。"),
                chart_card("PR 状态分布", plotly_chart(LensState.selected_pull_status_chart, LensState.project_chart_key), "观察当前项目 Pull Request 合并情况。"),
                columns="2",
                spacing="4",
                width="100%",
            ),
            rx.grid(
                chart_card("Issue 类型分布", plotly_chart(LensState.selected_issue_topic_chart, LensState.project_chart_key), "根据 Issue 标题类别汇总。"),
                chart_card("贡献者国家分布", plotly_chart(LensState.selected_country_chart, LensState.project_chart_key), "用于观察项目社区地域来源。"),
                columns="2",
                spacing="4",
                width="100%",
            ),
            spacing="5",
            align_items="stretch",
        )
    )
