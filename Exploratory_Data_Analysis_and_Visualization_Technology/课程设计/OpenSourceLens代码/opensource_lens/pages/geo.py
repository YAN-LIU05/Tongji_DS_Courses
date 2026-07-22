from __future__ import annotations

import reflex as rx

from ..components.chart_card import chart_card, plotly_chart
from ..components.layout import app_layout, page_header
from ..state import LensState

NOTE = "本页面地域数据来源于 GitHub 用户公开 profile 中的 location 字段。由于该字段由用户自行填写，可能存在缺失、模糊、不准确或虚构情况，因此地域可视化结果仅作为近似分析，不代表贡献者真实精确位置。"
GLOBALIZATION_COLUMNS = [
    {"id": "repo", "name": "项目"},
    {"id": "language", "name": "语言"},
    {"id": "stars", "name": "Stars"},
    {"id": "contributors", "name": "贡献者"},
    {"id": "country_count", "name": "国家数"},
    {"id": "city_count", "name": "城市数"},
    {"id": "globalization_score", "name": "国际化评分"},
]


def geo_country_tabs() -> rx.Component:
    return rx.tabs.root(
        rx.tabs.list(
            rx.tabs.trigger(LensState.quick_country_all_label, value="all"),
            rx.tabs.trigger(LensState.quick_country_1_label, value="country1"),
            rx.tabs.trigger(LensState.quick_country_2_label, value="country2"),
            rx.tabs.trigger(LensState.quick_country_3_label, value="country3"),
            width="100%",
            flex_wrap="wrap",
        ),
        rx.tabs.content(plotly_chart(LensState.geo_world_country_all_chart, LensState.geo_world_country_all_key), value="all"),
        rx.tabs.content(plotly_chart(LensState.geo_world_country_1_chart, LensState.geo_world_country_1_key), value="country1"),
        rx.tabs.content(plotly_chart(LensState.geo_world_country_2_chart, LensState.geo_world_country_2_key), value="country2"),
        rx.tabs.content(plotly_chart(LensState.geo_world_country_3_chart, LensState.geo_world_country_3_key), value="country3"),
        default_value="all",
        width="100%",
    )


def geo_language_tabs() -> rx.Component:
    return rx.tabs.root(
        rx.tabs.list(
            rx.tabs.trigger(LensState.quick_language_all_label, value="all"),
            rx.tabs.trigger(LensState.quick_language_1_label, value="lang1"),
            rx.tabs.trigger(LensState.quick_language_2_label, value="lang2"),
            rx.tabs.trigger(LensState.quick_language_3_label, value="lang3"),
            width="100%",
            flex_wrap="wrap",
        ),
        rx.tabs.content(plotly_chart(LensState.geo_world_language_all_chart, LensState.geo_world_language_all_key), value="all"),
        rx.tabs.content(plotly_chart(LensState.geo_world_language_1_chart, LensState.geo_world_language_1_key), value="lang1"),
        rx.tabs.content(plotly_chart(LensState.geo_world_language_2_chart, LensState.geo_world_language_2_key), value="lang2"),
        rx.tabs.content(plotly_chart(LensState.geo_world_language_3_chart, LensState.geo_world_language_3_key), value="lang3"),
        default_value="all",
        width="100%",
    )


def world_distribution_tabs() -> rx.Component:
    return rx.vstack(
        rx.text("国家快速视图", color="#6b7280", font_size="13px"),
        geo_country_tabs(),
        rx.text("语言快速视图", color="#6b7280", font_size="13px", margin_top="10px"),
        geo_language_tabs(),
        spacing="3",
        align_items="stretch",
        width="100%",
    )


def geo() -> rx.Component:
    return app_layout(
        rx.vstack(
            page_header("地域可视化", "观察贡献者国家、城市和项目国际化表现。"),
            rx.callout(NOTE, color_scheme="blue", width="100%"),
            rx.hstack(
                rx.select(LensState.geo_repo_options, value=LensState.selected_geo_repo, on_change=LensState.set_selected_geo_repo, placeholder="选择项目"),
                rx.select(LensState.country_options, value=LensState.selected_country, on_change=LensState.set_selected_country, placeholder="选择国家"),
                width="100%",
                wrap="wrap",
            ),
            rx.grid(
                chart_card("世界贡献者分布", world_distribution_tabs(), "全部/Top 3 国家与全部/Top 3 语言已预先绘制；原项目和国家下拉筛选仍保留用于下方其他图表。"),
                chart_card("城市气泡图", plotly_chart(LensState.city_bubble_chart, LensState.geo_chart_key), "城市经纬度来自 demo 映射或公开 location 解析。"),
                columns="2",
                spacing="4",
                width="100%",
            ),
            rx.grid(
                chart_card("国家贡献 Top 20", plotly_chart(LensState.country_top_chart, LensState.geo_chart_key), ""),
                chart_card("城市贡献 Top 20", plotly_chart(LensState.city_top_chart, LensState.geo_chart_key), ""),
                columns="2",
                spacing="4",
                width="100%",
            ),
            chart_card("项目-国家热力图", plotly_chart(LensState.project_country_heatmap_chart, LensState.geo_chart_key), "展示不同项目的地域社区结构。"),
            chart_card("国际化评分排名", rx.data_table(data=LensState.globalization_rank_rows, columns=GLOBALIZATION_COLUMNS, pagination=True, search=True), "按 globalization_score 排序查看。"),
            spacing="5",
            align_items="stretch",
        )
    )
