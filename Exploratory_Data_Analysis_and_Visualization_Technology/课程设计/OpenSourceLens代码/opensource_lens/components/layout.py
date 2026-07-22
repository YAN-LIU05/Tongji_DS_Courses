from __future__ import annotations

import reflex as rx

from .sidebar import sidebar
from ..state import LensState
from ..utils.style import MAIN_BG, MUTED, TEXT


def page_header(title: str, subtitle: str | None = None) -> rx.Component:
    return rx.hstack(
        rx.vstack(
            rx.heading(title, size="6", color=TEXT),
            rx.cond(subtitle is not None, rx.text(subtitle or "", color=MUTED)),
            rx.text(
                "数据源：",
                LensState.data_source,
                " ｜ 采集时间：",
                LensState.data_collected_at,
                " ｜ 模型训练：",
                LensState.model_trained_at,
                " ｜ 本地加载：",
                LensState.local_refreshed_at,
                color=MUTED,
                font_size="12px",
            ),
            rx.text(LensState.status_message, color=MUTED, font_size="12px"),
            spacing="1",
            align_items="start",
        ),
        rx.spacer(),
        rx.button("刷新本地数据", on_click=LensState.refresh_if_changed, variant="soft"),
        width="100%",
        align_items="center",
    )


def app_layout(content: rx.Component) -> rx.Component:
    return rx.box(
        sidebar(),
        rx.box(
            content,
            margin_left="240px",
            min_height="100vh",
            padding="28px",
            background=MAIN_BG,
            on_mount=LensState.load_data,
        ),
    )
