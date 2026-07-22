from __future__ import annotations

import reflex as rx

from ..utils.style import CARD_STYLE, MUTED, TEXT


def metric_card(label: str, value: str, hint: str = "") -> rx.Component:
    return rx.vstack(
        rx.text(label, color=MUTED, font_size="13px"),
        rx.heading(value, size="5", color=TEXT),
        rx.cond(hint != "", rx.text(hint, color=MUTED, font_size="12px")),
        padding="18px",
        min_height="112px",
        spacing="2",
        align_items="start",
        **CARD_STYLE,
    )

