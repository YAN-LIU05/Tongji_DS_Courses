from __future__ import annotations

import reflex as rx

from .pages.compare import compare
from .pages.dashboard import index
from .pages.geo import geo
from .pages.growth import growth
from .pages.ml_analysis import ml
from .pages.project_detail import project
from .pages.stars import stars
from .pages.statistics import statistics
from .pages.text_analysis import text
from .pages.trends import trends


app = rx.App(
    theme=rx.theme(
        appearance="light",
        accent_color="blue",
        radius="medium",
    )
)

app.add_page(index, route="/", title="首页总览")
app.add_page(project, route="/project", title="项目详情")
app.add_page(compare, route="/compare", title="项目对比")
app.add_page(geo, route="/geo", title="地域可视化")
app.add_page(statistics, route="/statistics", title="统计分布与相关性")
app.add_page(trends, route="/trends", title="时间序列趋势")
app.add_page(growth, route="/growth", title="GitHub Trending 实时榜")
app.add_page(stars, route="/stars", title="Stars 实时榜")
app.add_page(ml, route="/ml", title="机器学习分析")
app.add_page(text, route="/text", title="文本语义分析")
