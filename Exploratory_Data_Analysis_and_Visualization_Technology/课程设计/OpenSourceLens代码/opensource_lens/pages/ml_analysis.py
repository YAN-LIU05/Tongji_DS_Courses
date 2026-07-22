from __future__ import annotations

import reflex as rx

from ..components.chart_card import chart_card, plotly_chart
from ..components.layout import app_layout, page_header
from ..state import LensState

MODEL_NOTE = "本模块使用 K-Means 对开源项目进行无监督聚类，使用 PCA 将高维特征降至二维进行可视化，并使用 Isolation Forest 识别与大多数项目行为差异较大的异常项目。"
MODEL_METRIC_COLUMNS = [
    {"id": "metric", "name": "指标"},
    {"id": "value", "name": "数值"},
    {"id": "description", "name": "说明"},
]
CLUSTER_PROFILE_COLUMNS = [
    {"id": "cluster", "name": "聚类"},
    {"id": "cluster_label", "name": "聚类解释"},
    {"id": "project_count", "name": "项目数"},
    {"id": "representative_repo", "name": "代表项目"},
    {"id": "avg_popularity_score", "name": "平均热度"},
    {"id": "avg_activity_score", "name": "平均活跃"},
    {"id": "avg_health_score", "name": "平均健康"},
    {"id": "avg_globalization_score", "name": "平均国际化"},
    {"id": "description", "name": "解释说明"},
]


def ml() -> rx.Component:
    return app_layout(
        rx.vstack(
            page_header("机器学习分析", "聚类、降维和异常检测结果均由离线脚本生成。"),
            rx.callout(MODEL_NOTE, color_scheme="purple", width="100%"),
            rx.grid(
                chart_card("K-Means 聚类散点图", plotly_chart(LensState.cluster_scatter_chart, LensState.ml_chart_key), "PCA 二维坐标用于展示聚类结构。"),
                chart_card("Cluster 雷达图", plotly_chart(LensState.cluster_radar_chart, LensState.ml_chart_key), "展示不同聚类在核心评分上的均值。"),
                columns="2",
                spacing="4",
                width="100%",
            ),
            chart_card("Isolation Forest 异常检测", plotly_chart(LensState.anomaly_scatter_chart, LensState.ml_chart_key), "红色异常点代表行为与多数项目差异较大。"),
            rx.grid(
                chart_card("聚类平均指标热力图", plotly_chart(LensState.cluster_average_chart, LensState.ml_chart_key), "用颜色比较不同聚类在热度、活跃度、健康度和国际化上的平均表现。"),
                chart_card("风险项目可视化排行", plotly_chart(LensState.risk_project_chart, LensState.ml_chart_key), "按风险评分（1 - 健康度）展示需要优先关注的项目。"),
                columns="2",
                spacing="4",
                width="100%",
            ),
            rx.grid(
                chart_card("模型评估指标", rx.data_table(data=LensState.model_metrics_rows, columns=MODEL_METRIC_COLUMNS, pagination=True), "包含聚类数量、轮廓系数、PCA 解释率和异常占比；缺少新文件时显示可用的本地摘要。"),
                chart_card("聚类画像评分对比", plotly_chart(LensState.cluster_profile_chart, LensState.ml_chart_key), "比较不同聚类在热度、活跃度、健康度和国际化上的平均表现。"),
                columns="2",
                spacing="4",
                width="100%",
            ),
            chart_card("聚类解释表", rx.data_table(data=LensState.cluster_profile_rows, columns=CLUSTER_PROFILE_COLUMNS, pagination=True, search=True), "展示每个聚类的解释标签、代表项目和核心均值。"),
            spacing="5",
            align_items="stretch",
        )
    )
