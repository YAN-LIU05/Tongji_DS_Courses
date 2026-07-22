from __future__ import annotations

import reflex as rx


def status_badge(status: str) -> rx.Component:
    color = rx.match(
        status,
        ("anomaly", "red"),
        ("normal", "green"),
        ("high", "green"),
        ("medium", "amber"),
        ("low", "red"),
        "gray",
    )
    text = rx.match(
        status,
        ("anomaly", "异常"),
        ("normal", "正常"),
        ("high", "高"),
        ("medium", "中"),
        ("low", "低"),
        status,
    )
    return rx.badge(text, color_scheme=color, variant="soft")

