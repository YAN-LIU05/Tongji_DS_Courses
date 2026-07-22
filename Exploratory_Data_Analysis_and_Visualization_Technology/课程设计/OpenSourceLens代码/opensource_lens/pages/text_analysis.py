from __future__ import annotations

import reflex as rx

from ..components.chart_card import chart_card, plotly_chart
from ..components.layout import app_layout, page_header
from ..state import LensState


def text() -> rx.Component:
    return app_layout(
        rx.vstack(
            page_header("文本语义分析", "分析 README、Issue 和 Commit 文本主题结构。"),
            rx.grid(
                chart_card("README 语义嵌入散点图", plotly_chart(LensState.text_embedding_chart, LensState.text_chart_key), "优先使用 sentence-transformers，缺失时退化为 TF-IDF 或 demo 坐标。"),
                chart_card("Commit 类型分布", plotly_chart(LensState.commit_type_chart, LensState.text_chart_key), "fix、feat、docs、refactor、test、perf、chore。"),
                columns="2",
                spacing="4",
                width="100%",
            ),
            chart_card("项目相似度热力图", plotly_chart(LensState.text_similarity_chart, LensState.text_chart_key), "优先读取 text_similarity.csv 中的高维文本向量余弦相似度；缺失时退化为二维语义坐标近似，项目较多时展示 Stars 最高的前 80 个。"),
            chart_card("Issue 主题分布", plotly_chart(LensState.issue_topic_chart, LensState.text_chart_key), "Bug、Feature Request、Documentation 等类别。"),
            spacing="5",
            align_items="stretch",
        )
    )
