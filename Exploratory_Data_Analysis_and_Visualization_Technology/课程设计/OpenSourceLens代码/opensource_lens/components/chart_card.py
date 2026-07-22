from __future__ import annotations

import reflex as rx

from ..utils.style import CARD_STYLE, MUTED, TEXT

PLOTLY_CONFIG = {
    "responsive": True,
    "displayModeBar": False,
    "scrollZoom": False,
}


def empty_state(message: str = "暂无数据，请先生成 data/processed/ 下的 CSV 文件。") -> rx.Component:
    return rx.center(rx.text(message, color=MUTED), min_height="260px", **CARD_STYLE)


def plotly_chart(data, refresh_key=None) -> rx.Component:
    props = {
        "data": data,
        "config": PLOTLY_CONFIG,
        "width": "100%",
    }
    if refresh_key is not None:
        props["key"] = refresh_key
    return rx.plotly(**props)


def chart_card(title: str, chart: rx.Component, description: str = "") -> rx.Component:
    return rx.vstack(
        rx.heading(title, size="4", color=TEXT),
        chart,
        rx.cond(description != "", rx.text(description, color=MUTED, font_size="13px")),
        width="100%",
        padding="18px",
        spacing="3",
        align_items="stretch",
        **CARD_STYLE,
    )
