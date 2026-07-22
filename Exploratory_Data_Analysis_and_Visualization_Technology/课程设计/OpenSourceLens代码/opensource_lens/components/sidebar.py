from __future__ import annotations

import reflex as rx

from ..utils.style import SIDEBAR_BG


NAV_ITEMS = [
    ("首页总览", "/"),
    ("项目详情", "/project"),
    ("项目对比", "/compare"),
    ("地域可视化", "/geo"),
    ("统计分布与相关性", "/statistics"),
    ("时间序列趋势", "/trends"),
    ("Trending 实时榜", "/growth"),
    ("Stars 实时榜", "/stars"),
    ("机器学习分析", "/ml"),
    ("文本语义分析", "/text"),
]


def sidebar() -> rx.Component:
    return rx.vstack(
        rx.heading("OpenSourceLens", size="5", color="white"),
        rx.text("开源项目智能可视化分析平台", color="#cbd5e1", font_size="13px"),
        rx.divider(border_color="#334155"),
        *[
            rx.link(
                label,
                href=route,
                color="#e5e7eb",
                padding="10px 12px",
                border_radius="6px",
                width="100%",
                _hover={"background": "#1f2937", "text_decoration": "none"},
            )
            for label, route in NAV_ITEMS
        ],
        position="fixed",
        left="0",
        top="0",
        bottom="0",
        width="240px",
        padding="22px 18px",
        spacing="3",
        align_items="stretch",
        background=SIDEBAR_BG,
        z_index="10",
    )
