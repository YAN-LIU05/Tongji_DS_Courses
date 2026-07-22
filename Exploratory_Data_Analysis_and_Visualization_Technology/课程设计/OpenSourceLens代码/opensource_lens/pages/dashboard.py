from __future__ import annotations

import reflex as rx

from ..components.chart_card import chart_card, plotly_chart
from ..components.layout import app_layout, page_header
from ..components.metric_card import metric_card
from ..components.project_table import project_table
from ..state import LensState


def dashboard_language_tabs() -> rx.Component:
    return rx.tabs.root(
        rx.tabs.list(
            rx.tabs.trigger(LensState.quick_language_all_label, value="all"),
            rx.tabs.trigger(LensState.quick_language_1_label, value="lang1"),
            rx.tabs.trigger(LensState.quick_language_2_label, value="lang2"),
            rx.tabs.trigger(LensState.quick_language_3_label, value="lang3"),
            width="100%",
            flex_wrap="wrap",
        ),
        rx.tabs.content(plotly_chart(LensState.dashboard_ecosystem_language_all_chart, LensState.dashboard_ecosystem_language_all_key), value="all"),
        rx.tabs.content(plotly_chart(LensState.dashboard_ecosystem_language_1_chart, LensState.dashboard_ecosystem_language_1_key), value="lang1"),
        rx.tabs.content(plotly_chart(LensState.dashboard_ecosystem_language_2_chart, LensState.dashboard_ecosystem_language_2_key), value="lang2"),
        rx.tabs.content(plotly_chart(LensState.dashboard_ecosystem_language_3_chart, LensState.dashboard_ecosystem_language_3_key), value="lang3"),
        default_value="all",
        width="100%",
    )


def index() -> rx.Component:
    return app_layout(
        rx.vstack(
            page_header("首页总览", "从热度、活跃度、健康度和国际化观察开源项目生态。"),
            rx.hstack(
                rx.select(LensState.language_options, value=LensState.selected_language, on_change=LensState.set_selected_language, placeholder="选择语言"),
                rx.input(placeholder="搜索项目", value=LensState.search_keyword, on_change=LensState.set_search_keyword, debounce_timeout=450),
                rx.input(type="number", placeholder="最低 Stars", value=LensState.star_min, on_change=LensState.set_star_min, debounce_timeout=450),
                rx.input(type="number", placeholder="最高 Stars", value=LensState.star_max, on_change=LensState.set_star_max, debounce_timeout=450),
                rx.input(type="number", step="0.05", min="0", max="1", placeholder="最低健康度", value=LensState.health_min, on_change=LensState.set_health_min, debounce_timeout=450),
                rx.input(type="number", step="0.05", min="0", max="1", placeholder="最低活跃度", value=LensState.activity_min, on_change=LensState.set_activity_min, debounce_timeout=450),
                width="100%",
                wrap="wrap",
            ),
            rx.grid(
                rx.foreach(LensState.dashboard_metrics, lambda item: metric_card(item["label"], item["value"], item["hint"])),
                columns="4",
                spacing="4",
                width="100%",
            ),
            chart_card(
                "开源生态总览大图",
                dashboard_language_tabs(),
                "全部语言和项目数最多的前三个语言已预先绘制；原语言下拉筛选仍保留用于下方其他图表和项目列表。",
            ),
            rx.grid(
                chart_card("语言生态树图", plotly_chart(LensState.language_treemap_chart, LensState.dashboard_chart_key), "用面积展示不同语言和项目的 Stars 规模，用颜色观察健康度差异。"),
                chart_card("头部项目评分热力图", plotly_chart(LensState.score_heatmap_chart, LensState.dashboard_chart_key), "比较头部项目在热度、活跃度、健康度、国际化上的结构差异。"),
                columns="2",
                spacing="4",
                width="100%",
            ),
            rx.grid(
                chart_card("语言分布", plotly_chart(LensState.language_chart, LensState.dashboard_chart_key), "展示样本项目的主语言结构。"),
                chart_card("Stars-Forks 关系", plotly_chart(LensState.star_fork_chart, LensState.dashboard_chart_key), "观察关注度和复用规模的关系，气泡大小代表贡献者数量。"),
                columns="2",
                spacing="4",
                width="100%",
            ),
            rx.grid(
                chart_card("Stars 总数排行", plotly_chart(LensState.star_bar_chart, LensState.dashboard_chart_key), "按当前 Stars 总数展示头部项目。"),
                chart_card("发布一年后 Stars 数量排行", plotly_chart(LensState.first_year_star_chart, LensState.dashboard_chart_key), "GitHub API 不提供历史首年 Stars；此图基于项目创建时间、采集时间和当前 Stars 离线估算，用于比较早期增长势能。"),
                columns="2",
                spacing="4",
                width="100%",
            ),
            rx.vstack(
                rx.heading("国家地域可视化", size="5"),
                rx.callout(
                    "地域数据来自 GitHub 用户公开 location 字段，存在缺失、模糊或不准确情况；首页展示全量项目的国家与城市分布。",
                    color_scheme="blue",
                    width="100%",
                ),
                rx.grid(
                    chart_card("世界贡献者分布", plotly_chart(LensState.dashboard_world_map_chart, LensState.dashboard_chart_key), "按国家汇总全量贡献者样本。"),
                    chart_card("城市气泡图", plotly_chart(LensState.dashboard_city_bubble_chart, LensState.dashboard_chart_key), "按城市经纬度展示贡献者集中区域。"),
                    columns="2",
                    spacing="4",
                    width="100%",
                ),
                rx.grid(
                    chart_card("国家贡献 Top 20", plotly_chart(LensState.dashboard_country_top_chart, LensState.dashboard_chart_key), "展示贡献量最高的国家。"),
                    chart_card("城市贡献 Top 20", plotly_chart(LensState.dashboard_city_top_chart, LensState.dashboard_chart_key), "展示贡献量最高的城市。"),
                    columns="2",
                    spacing="4",
                    width="100%",
                ),
                chart_card("项目-国家热力图", plotly_chart(LensState.dashboard_project_country_heatmap_chart, LensState.dashboard_chart_key), "展示全量项目的地域社区结构。"),
                spacing="4",
                align_items="stretch",
                width="100%",
            ),
            chart_card("项目列表", project_table(LensState.filtered_scores_preview), "筛选器会影响列表展示；为保证交互速度，列表展示 Stars 最高的前 80 个项目。"),
            spacing="5",
            align_items="stretch",
        )
    )
