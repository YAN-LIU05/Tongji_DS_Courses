from __future__ import annotations

import reflex as rx

from ..components.chart_card import chart_card, plotly_chart
from ..components.layout import app_layout, page_header
from ..state import LensState


DISTRIBUTION_METRICS = ["Stars", "Forks", "Open Issues", "贡献者", "热度评分", "活跃度评分", "健康度评分", "国际化评分"]


def language_score_tabs() -> rx.Component:
    return rx.tabs.root(
        rx.tabs.list(
            rx.tabs.trigger("热度评分", value="popularity"),
            rx.tabs.trigger("活跃度评分", value="activity"),
            rx.tabs.trigger("健康度评分", value="health"),
            rx.tabs.trigger("国际化评分", value="globalization"),
            width="100%",
            flex_wrap="wrap",
        ),
        rx.tabs.content(
            plotly_chart(LensState.language_popularity_score_box_chart, LensState.statistics_language_popularity_chart_key),
            value="popularity",
        ),
        rx.tabs.content(
            plotly_chart(LensState.language_activity_score_box_chart, LensState.statistics_language_activity_chart_key),
            value="activity",
        ),
        rx.tabs.content(
            plotly_chart(LensState.language_health_score_box_chart, LensState.statistics_language_health_chart_key),
            value="health",
        ),
        rx.tabs.content(
            plotly_chart(LensState.language_globalization_score_box_chart, LensState.statistics_language_globalization_chart_key),
            value="globalization",
        ),
        default_value="health",
        width="100%",
    )


def statistics() -> rx.Component:
    return app_layout(
        rx.vstack(
            page_header("统计分布与相关性", "用分布、箱线图和相关性热力图补充探索性数据分析。"),
            rx.hstack(
                rx.select(LensState.language_options, value=LensState.selected_language, on_change=LensState.set_selected_language, placeholder="选择语言"),
                rx.input(placeholder="搜索项目", value=LensState.search_keyword, on_change=LensState.set_search_keyword, debounce_timeout=450),
                rx.text("分布指标", color="#6b7280"),
                rx.select(DISTRIBUTION_METRICS, value=LensState.selected_distribution_metric, on_change=LensState.set_selected_distribution_metric),
                width="100%",
                wrap="wrap",
                align_items="center",
            ),
            rx.grid(
                chart_card("指标统计分布", plotly_chart(LensState.metric_distribution_chart, LensState.statistics_metric_chart_key), "对长尾指标自动使用 log10 变换，并保留更充足的纵向空间观察分布形态。"),
                chart_card("核心评分箱线分布", plotly_chart(LensState.score_distribution_chart, LensState.statistics_score_chart_key), "比较热度、活跃度、健康度、国际化评分的整体分布和离群情况。"),
                columns="2",
                spacing="4",
                width="100%",
            ),
            rx.grid(
                chart_card("语言分组评分分布", language_score_tabs(), "四个评分图已在卡片内预先生成，切换指标不会触发后端重算。"),
                chart_card("核心指标相关性热力图", plotly_chart(LensState.correlation_heatmap_chart, LensState.statistics_correlation_chart_key), "用 Pearson 相关系数观察规模、活跃、健康和国际化指标之间的线性关系。"),
                columns="2",
                spacing="4",
                width="100%",
            ),
            spacing="5",
            align_items="stretch",
        )
    )
