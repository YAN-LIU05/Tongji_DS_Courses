from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


COLORS = ["#2563eb", "#0891b2", "#7c3aed", "#059669", "#d97706", "#dc2626", "#4f46e5", "#0f766e"]
TEMPLATE = "plotly_white"


def _legend_settings(fig: go.Figure) -> tuple[dict, int, int]:
    legend_count = 0
    for trace in fig.data:
        name = str(getattr(trace, "name", "") or "")
        showlegend = getattr(trace, "showlegend", None)
        if name and name not in {"<br>", "None"} and showlegend is not False:
            legend_count += 1
    if legend_count == 0:
        return {}, 35, 0
    extra_height = 90 if legend_count > 12 else 45
    bottom_margin = 150 if legend_count > 12 else 105
    return (
        {
            "orientation": "h",
            "yanchor": "top",
            "y": -0.18,
            "xanchor": "left",
            "x": 0,
            "title": None,
            "font": {"size": 12},
            "itemsizing": "constant",
        },
        bottom_margin,
        extra_height,
    )


def empty_figure(message: str = "暂无可视化数据") -> go.Figure:
    fig = go.Figure()
    fig.add_annotation(text=message, x=0.5, y=0.5, showarrow=False, font={"size": 16, "color": "#6b7280"})
    fig.update_layout(height=360, margin=dict(l=20, r=20, t=40, b=20), paper_bgcolor="white", plot_bgcolor="white", template=TEMPLATE)
    return fig


def finish(fig: go.Figure, height: int = 360) -> go.Figure:
    legend, bottom_margin, extra_height = _legend_settings(fig)
    fig.update_layout(
        height=height + extra_height,
        margin=dict(l=30, r=20, t=35, b=bottom_margin),
        paper_bgcolor="white",
        plot_bgcolor="white",
        template=TEMPLATE,
        font=dict(family="Arial, Microsoft YaHei, sans-serif", color="#111827"),
        legend=legend,
        title_text=None,
        hoverlabel=dict(bgcolor="white", font_size=12),
    )
    fig.update_xaxes(showgrid=True, gridcolor="#eef2f7", zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor="#eef2f7", zeroline=False)
    return fig


def _top(df: pd.DataFrame, value: str, n: int = 10) -> pd.DataFrame:
    if df.empty or value not in df.columns:
        return pd.DataFrame()
    return df.sort_values(value, ascending=False).head(n)


def _sample(df: pd.DataFrame, n: int = 300, sort_col: str = "stars") -> pd.DataFrame:
    if df.empty or len(df) <= n:
        return df
    if sort_col in df.columns:
        work = df.copy()
        work[sort_col] = pd.to_numeric(work[sort_col], errors="coerce").fillna(0)
        return work.sort_values(sort_col, ascending=False).head(n)
    return df.head(n)


def make_star_bar(df: pd.DataFrame) -> go.Figure:
    top = _top(df, "stars")
    if top.empty:
        return empty_figure()
    top = top.copy()
    top["stars"] = pd.to_numeric(top["stars"], errors="coerce").fillna(0)
    top = top.sort_values("stars", ascending=False)
    fig = px.bar(
        top,
        x="stars",
        y="name",
        orientation="h",
        title="Stars 总数 Top 10",
        labels={"stars": "Stars 总数", "name": "项目"},
        color="stars",
        color_continuous_scale="Blues",
        hover_data=[col for col in ["repo", "forks", "contributors", "language"] if col in top.columns],
        text="stars",
    )
    fig.update_traces(texttemplate="%{text:,}", textposition="outside", cliponaxis=False)
    fig.update_yaxes(categoryorder="array", categoryarray=top["name"].tolist(), autorange="reversed")
    return finish(fig, height=420)


def make_first_year_star_bar(df: pd.DataFrame) -> go.Figure:
    if df.empty or "stars" not in df.columns:
        return empty_figure()
    work = df.copy()
    work["stars"] = pd.to_numeric(work["stars"], errors="coerce").fillna(0)
    if "stars_first_year_estimate" not in work.columns:
        if "created_at" not in work.columns:
            return empty_figure("缺少 created_at，无法计算发布一年后 Stars")
        created = pd.to_datetime(work["created_at"], errors="coerce", utc=True)
        if "collected_at" in work.columns:
            collected = pd.to_datetime(work["collected_at"], errors="coerce", utc=True)
        else:
            collected = pd.Series(pd.NaT, index=work.index, dtype="datetime64[ns, UTC]")
        collected = collected.fillna(pd.Timestamp.now(tz="UTC"))
        age_days = (collected - created).dt.total_seconds().div(86400).clip(lower=1).fillna(1)
        work["repo_age_days"] = age_days.round().astype(int)
        work["stars_first_year_estimate"] = (work["stars"] * 365 / age_days).clip(upper=work["stars"]).round()
        work["first_year_window_observed"] = age_days >= 365
    work["stars_first_year_estimate"] = pd.to_numeric(work["stars_first_year_estimate"], errors="coerce").fillna(0)
    top = work.sort_values("stars_first_year_estimate", ascending=False).head(10).copy()
    if top.empty or top["stars_first_year_estimate"].max() <= 0:
        return empty_figure("暂无可用于计算发布一年后 Stars 的数据")
    observed_count = top.get("first_year_window_observed", pd.Series(False, index=top.index)).astype(str).str.lower().isin(["true", "1", "yes"]).sum()
    title = "发布一年后 Stars 规模 Top 10（离线估算）"
    if observed_count == 0:
        title = "发布一年后 Stars 规模 Top 10（按当前年龄估算）"
    fig = px.bar(
        top,
        x="stars_first_year_estimate",
        y="name",
        orientation="h",
        title=title,
        labels={"stars_first_year_estimate": "发布一年后 Stars", "name": "项目"},
        color="stars_first_year_estimate",
        color_continuous_scale="Tealgrn",
        hover_data=[col for col in ["repo", "stars", "repo_age_days", "created_at", "language"] if col in top.columns],
        text="stars_first_year_estimate",
    )
    fig.update_traces(texttemplate="%{text:,}", textposition="outside", cliponaxis=False)
    fig.update_yaxes(categoryorder="array", categoryarray=top["name"].tolist(), autorange="reversed")
    return finish(fig, height=420)


def make_fork_bar(df: pd.DataFrame) -> go.Figure:
    top = _top(df, "forks")
    if top.empty:
        return empty_figure()
    fig = px.bar(top.sort_values("forks"), x="forks", y="name", orientation="h", title="Forks Top 10", labels={"forks": "Forks", "name": "项目"}, color_discrete_sequence=[COLORS[1]], hover_data=["repo", "stars", "contributors"])
    return finish(fig)


def make_star_fork_scatter(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return empty_figure()
    df = _sample(df, n=300).copy()
    df["stars"] = pd.to_numeric(df.get("stars", 0), errors="coerce").fillna(0)
    df["forks"] = pd.to_numeric(df.get("forks", 0), errors="coerce").fillna(0)
    fig = px.scatter(df, x="stars", y="forks", size="contributors", color="language", hover_name="repo", title="Stars 与 Forks 关系", labels={"stars": "Stars", "forks": "Forks", "contributors": "贡献者", "language": "语言"}, hover_data=["health_score", "activity_score"])
    fit_data = df[(df["stars"] > 0) & (df["forks"] >= 0)].sort_values("stars")
    if len(fit_data) >= 2 and fit_data["stars"].nunique() >= 2:
        slope, intercept = np.polyfit(fit_data["stars"], fit_data["forks"], 1)
        x_values = np.array([fit_data["stars"].min(), fit_data["stars"].max()])
        y_values = slope * x_values + intercept
        fig.add_trace(
            go.Scatter(
                x=x_values,
                y=y_values,
                mode="lines",
                name="拟合趋势线",
                line=dict(color="#111827", width=2, dash="dash"),
                hovertemplate="Stars: %{x:,.0f}<br>预测 Forks: %{y:,.0f}<extra></extra>",
            )
        )
    return finish(fig)


def make_language_distribution(df: pd.DataFrame) -> go.Figure:
    if df.empty or "language" not in df.columns:
        return empty_figure()
    counts = df["language"].fillna("Unknown").value_counts().reset_index()
    counts.columns = ["language", "count"]
    fig = px.pie(counts, names="language", values="count", title="主要语言分布", color_discrete_sequence=COLORS, hole=0.42)
    fig.update_traces(textposition="inside", textinfo="percent+label")
    return finish(fig)


def make_created_year_bar(df: pd.DataFrame) -> go.Figure:
    if df.empty or "created_at" not in df.columns:
        return empty_figure()
    years = pd.to_datetime(df["created_at"], errors="coerce").dt.year.value_counts().sort_index().reset_index()
    years.columns = ["year", "count"]
    return finish(px.bar(years, x="year", y="count", title="项目创建年份分布", labels={"year": "创建年份", "count": "项目数"}, color_discrete_sequence=[COLORS[4]]))


def make_quadrant_scatter(df: pd.DataFrame) -> go.Figure:
    if df.empty or not {"popularity_score", "activity_score"}.issubset(df.columns):
        return empty_figure()
    fig = px.scatter(df, x="popularity_score", y="activity_score", color="health_score", size="stars", hover_name="repo", title="热度-活跃度四象限", labels={"popularity_score": "热度评分", "activity_score": "活跃度评分", "health_score": "健康度评分", "stars": "Stars"}, color_continuous_scale="Blues")
    fig.add_vline(x=df["popularity_score"].median(), line_dash="dash", line_color="#9ca3af")
    fig.add_hline(y=df["activity_score"].median(), line_dash="dash", line_color="#9ca3af")
    return finish(fig)


def make_ecosystem_bubble(df: pd.DataFrame) -> go.Figure:
    if df.empty or not {"activity_score", "health_score", "stars"}.issubset(df.columns):
        return empty_figure()
    df = _sample(df, n=300)
    fig = px.scatter(
        df,
        x="activity_score",
        y="health_score",
        size="stars",
        color="globalization_score" if "globalization_score" in df.columns else "stars",
        hover_name="repo",
        hover_data=["language", "stars", "forks", "contributors", "popularity_score"],
        title="开源项目生态大图：活跃度 × 健康度 × 热度",
        labels={
            "activity_score": "活跃度评分",
            "health_score": "健康度评分",
            "globalization_score": "国际化评分",
            "stars": "Stars",
            "forks": "Forks",
            "contributors": "贡献者",
            "language": "语言",
            "popularity_score": "热度评分",
        },
        color_continuous_scale="Viridis",
        size_max=58,
    )
    fig.add_hline(y=df["health_score"].median(), line_dash="dash", line_color="#94a3b8")
    fig.add_vline(x=df["activity_score"].median(), line_dash="dash", line_color="#94a3b8")
    fig.add_annotation(text="高活跃 / 高健康", x=0.98, y=0.98, xref="paper", yref="paper", showarrow=False, font={"color": "#047857", "size": 13})
    fig.add_annotation(text="低活跃 / 需关注", x=0.02, y=0.05, xref="paper", yref="paper", showarrow=False, font={"color": "#b45309", "size": 13})
    return finish(fig, height=560)


def make_language_treemap(df: pd.DataFrame) -> go.Figure:
    if df.empty or "language" not in df.columns:
        return empty_figure()
    work = _sample(df, n=180).copy()
    work["language"] = work["language"].fillna("Unknown").replace("", "Unknown")
    work["stars"] = pd.to_numeric(work.get("stars", 0), errors="coerce").fillna(0)
    fig = px.treemap(
        work,
        path=["language", "repo"],
        values="stars",
        color="health_score" if "health_score" in work.columns else "stars",
        color_continuous_scale="Tealgrn",
        title="语言生态树图：Stars 规模与健康度",
        hover_data=["forks", "contributors", "activity_score", "globalization_score"],
    )
    fig.update_traces(root_color="#f8fafc")
    return finish(fig, height=430)


def make_score_heatmap(df: pd.DataFrame) -> go.Figure:
    cols = ["popularity_score", "activity_score", "health_score", "globalization_score"]
    if df.empty or not set(cols).issubset(df.columns):
        return empty_figure()
    top = df.sort_values("stars", ascending=False).head(30).copy()
    top = top.set_index("repo")[cols]
    fig = px.imshow(
        top,
        aspect="auto",
        title="头部项目评分热力图",
        labels={"x": "评分维度", "y": "项目", "color": "评分"},
        color_continuous_scale="Blues",
        zmin=0,
        zmax=1,
    )
    fig.update_xaxes(ticktext=["热度", "活跃", "健康", "国际化"], tickvals=cols)
    return finish(fig, height=430)


DISTRIBUTION_METRICS = {
    "Stars": "stars",
    "Forks": "forks",
    "Open Issues": "open_issues",
    "贡献者": "contributors",
    "热度评分": "popularity_score",
    "活跃度评分": "activity_score",
    "健康度评分": "health_score",
    "国际化评分": "globalization_score",
}


def _metric_column(label: str) -> str:
    return DISTRIBUTION_METRICS.get(label, "stars")


def make_metric_distribution(df: pd.DataFrame, metric_label: str = "Stars") -> go.Figure:
    col = _metric_column(metric_label)
    if df.empty or col not in df.columns:
        return empty_figure("暂无可用于统计分布的数据")
    work = df.copy()
    work[col] = pd.to_numeric(work[col], errors="coerce").fillna(0)
    if work[col].max() > 100:
        work["_display_value"] = np.log10(work[col] + 1)
        x_label = f"log10({metric_label} + 1)"
    else:
        work["_display_value"] = work[col]
        x_label = metric_label
    fig = px.histogram(
        work,
        x="_display_value",
        nbins=28,
        color="language" if "language" in work.columns else None,
        title=f"{metric_label} 统计分布",
        labels={"_display_value": x_label, "count": "项目数", "language": "语言"},
        hover_data=[field for field in ["repo", col, "language", "health_score", "activity_score"] if field in work.columns],
        color_discrete_sequence=COLORS,
    )
    fig.update_layout(bargap=0.08)
    return finish(fig, height=520)


def make_score_distribution(df: pd.DataFrame) -> go.Figure:
    cols = ["popularity_score", "activity_score", "health_score", "globalization_score"]
    if df.empty or not set(cols).issubset(df.columns):
        return empty_figure("暂无评分分布数据")
    names = {"popularity_score": "热度", "activity_score": "活跃", "health_score": "健康", "globalization_score": "国际化"}
    long_df = df[["repo"] + cols].copy()
    for col in cols:
        long_df[col] = pd.to_numeric(long_df[col], errors="coerce").fillna(0)
    long_df = long_df.melt(id_vars="repo", value_vars=cols, var_name="评分维度", value_name="评分")
    long_df["评分维度"] = long_df["评分维度"].map(names)
    fig = px.box(
        long_df,
        x="评分维度",
        y="评分",
        color="评分维度",
        points="outliers",
        title="核心评分箱线分布",
        labels={"评分": "评分（0-1）"},
        color_discrete_sequence=COLORS,
        hover_data=["repo"],
    )
    fig.update_yaxes(range=[0, 1])
    return finish(fig, height=420)


def make_language_score_box(df: pd.DataFrame, metric_label: str = "健康度评分") -> go.Figure:
    col = _metric_column(metric_label)
    if df.empty or col not in df.columns or "language" not in df.columns:
        return empty_figure("暂无语言分组评分数据")
    work = df.copy()
    work[col] = pd.to_numeric(work[col], errors="coerce").fillna(0)
    work["language"] = work["language"].fillna("Unknown").replace("", "Unknown")
    top_languages = work["language"].value_counts().head(12).index
    work = work[work["language"].isin(top_languages)]
    fig = px.box(
        work,
        x="language",
        y=col,
        color="language",
        points="outliers",
        title=f"不同语言的 {metric_label} 分布",
        labels={"language": "语言", col: metric_label},
        hover_data=["repo", "stars", "forks"],
        color_discrete_sequence=COLORS,
    )
    if col.endswith("_score"):
        fig.update_yaxes(range=[0, 1])
    fig = finish(fig, height=450)
    fig.update_layout(
        legend=dict(y=-0.32, yanchor="top"),
        margin=dict(l=30, r=20, t=35, b=175),
    )
    return fig


def make_correlation_heatmap(df: pd.DataFrame) -> go.Figure:
    cols = [
        "stars",
        "forks",
        "watchers",
        "open_issues",
        "contributors",
        "commits_recent",
        "issues_recent",
        "prs_recent",
        "issue_close_rate",
        "pr_merge_rate",
        "popularity_score",
        "activity_score",
        "health_score",
        "globalization_score",
    ]
    available = [col for col in cols if col in df.columns]
    if df.empty or len(available) < 2:
        return empty_figure("暂无可用于相关性分析的数据")
    work = df[available].apply(pd.to_numeric, errors="coerce").fillna(0)
    corr = work.corr().fillna(0)
    labels = {
        "stars": "Stars",
        "forks": "Forks",
        "watchers": "Watchers",
        "open_issues": "Open Issues",
        "contributors": "贡献者",
        "commits_recent": "近期提交",
        "issues_recent": "近期 Issue",
        "prs_recent": "近期 PR",
        "issue_close_rate": "Issue 关闭率",
        "pr_merge_rate": "PR 合并率",
        "popularity_score": "热度",
        "activity_score": "活跃",
        "health_score": "健康",
        "globalization_score": "国际化",
    }
    corr.index = [labels.get(value, value) for value in corr.index]
    corr.columns = [labels.get(value, value) for value in corr.columns]
    fig = px.imshow(
        corr,
        zmin=-1,
        zmax=1,
        text_auto=".2f",
        aspect="auto",
        title="核心指标相关性热力图",
        labels={"x": "指标", "y": "指标", "color": "相关系数"},
        color_continuous_scale="RdBu",
    )
    fig.update_xaxes(tickangle=35)
    return finish(fig, height=560)


def make_project_radar(row: dict) -> go.Figure:
    if not row:
        return empty_figure()
    labels = ["热度", "活跃", "健康", "国际化"]
    values = [row.get("popularity_score", 0), row.get("activity_score", 0), row.get("health_score", 0), row.get("globalization_score", 0)]
    fig = go.Figure(go.Scatterpolar(r=values + [values[0]], theta=labels + [labels[0]], fill="toself", name=row.get("name", "项目")))
    fig.update_polars(radialaxis=dict(visible=True, range=[0, 1]))
    fig.update_layout(title="项目综合雷达图")
    return finish(fig)


def make_recent_activity_bar(row: dict) -> go.Figure:
    if not row:
        return empty_figure()
    df = pd.DataFrame(
        [
            {"指标": "近期提交", "数量": row.get("commits_recent", 0)},
            {"指标": "近期 Issue", "数量": row.get("issues_recent", 0)},
            {"指标": "近期 PR", "数量": row.get("prs_recent", 0)},
        ]
    )
    return finish(px.bar(df, x="指标", y="数量", title="近期协作活动概览", color="指标", color_discrete_sequence=COLORS))


def make_issue_status_chart(df: pd.DataFrame) -> go.Figure:
    if df.empty or "state" not in df.columns:
        return empty_figure()
    counts = df["state"].fillna("unknown").value_counts().reset_index()
    counts.columns = ["状态", "数量"]
    names = {"open": "未关闭", "closed": "已关闭", "unknown": "未知"}
    counts["状态"] = counts["状态"].map(lambda value: names.get(value, value))
    return finish(px.pie(counts, names="状态", values="数量", title="Issue 状态分布", color_discrete_sequence=[COLORS[5], COLORS[3], COLORS[1]], hole=0.45))


def make_pull_status_chart(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return empty_figure()
    data = pd.DataFrame(
        [
            {"状态": "已合并", "数量": int(df.get("merged_at", pd.Series(dtype=str)).fillna("").astype(str).str.len().gt(0).sum())},
            {"状态": "已关闭未合并", "数量": int(((df.get("state", pd.Series(dtype=str)) == "closed") & df.get("merged_at", pd.Series(dtype=str)).fillna("").astype(str).str.len().eq(0)).sum())},
            {"状态": "仍在开放", "数量": int((df.get("state", pd.Series(dtype=str)) == "open").sum())},
        ]
    )
    return finish(px.bar(data, x="状态", y="数量", title="Pull Request 状态分布", color="状态", color_discrete_sequence=[COLORS[3], COLORS[4], COLORS[0]]))


def make_score_compare_bar(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return empty_figure()
    cols = ["popularity_score", "activity_score", "health_score", "globalization_score"]
    long_df = df[["repo"] + cols].melt(id_vars="repo", var_name="指标", value_name="评分")
    names = {"popularity_score": "热度", "activity_score": "活跃", "health_score": "健康", "globalization_score": "国际化"}
    long_df["指标"] = long_df["指标"].map(names)
    return finish(px.bar(long_df, x="repo", y="评分", color="指标", barmode="group", title="项目评分对比", color_discrete_sequence=COLORS))


def make_rate_compare_bar(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return empty_figure()
    cols = [col for col in ["issue_close_rate", "pr_merge_rate"] if col in df.columns]
    if not cols:
        return empty_figure()
    long_df = df[["repo"] + cols].melt(id_vars="repo", var_name="指标", value_name="比例")
    names = {"issue_close_rate": "Issue 关闭率", "pr_merge_rate": "PR 合并率"}
    long_df["指标"] = long_df["指标"].map(names)
    return finish(px.bar(long_df, x="repo", y="比例", color="指标", barmode="group", title="协作效率对比", labels={"repo": "项目", "比例": "比例"}, color_discrete_sequence=[COLORS[3], COLORS[6]]))


def make_multi_project_radar(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return empty_figure()
    labels = ["热度", "活跃", "健康", "国际化"]
    fig = go.Figure()
    for _, row in df.iterrows():
        values = [row.get("popularity_score", 0), row.get("activity_score", 0), row.get("health_score", 0), row.get("globalization_score", 0)]
        fig.add_trace(go.Scatterpolar(r=values + [values[0]], theta=labels + [labels[0]], fill="toself", name=row.get("name", row.get("repo"))))
    fig.update_polars(radialaxis=dict(visible=True, range=[0, 1]))
    fig.update_layout(title="多项目雷达对比")
    return finish(fig)


def make_world_map(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return empty_figure()
    country = df.groupby("country", as_index=False)["contributions"].sum()
    fig = px.choropleth(country, locations="country", locationmode="country names", color="contributions", title="贡献者国家分布", labels={"contributions": "贡献数"}, color_continuous_scale="Blues")
    return finish(fig, height=420)


def make_city_bubble_map(df: pd.DataFrame) -> go.Figure:
    if df.empty or not {"lat", "lon"}.issubset(df.columns):
        return empty_figure()
    city = df.groupby(["country", "city", "lat", "lon"], as_index=False)["contributions"].sum()
    city = city.sort_values("contributions", ascending=False).head(300)
    fig = px.scatter_geo(city, lat="lat", lon="lon", size="contributions", hover_name="city", color="country", title="城市贡献者气泡图", labels={"contributions": "贡献数", "country": "国家"})
    return finish(fig, height=420)


def make_country_top_bar(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return empty_figure()
    country = df.groupby("country", as_index=False)["contributions"].sum().sort_values("contributions", ascending=False).head(20)
    return finish(px.bar(country.sort_values("contributions"), x="contributions", y="country", orientation="h", title="国家贡献 Top 20", labels={"contributions": "贡献数", "country": "国家"}, color_discrete_sequence=[COLORS[0]]))


def make_city_top_bar(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return empty_figure()
    city = df.groupby("city", as_index=False)["contributions"].sum().sort_values("contributions", ascending=False).head(20)
    return finish(px.bar(city.sort_values("contributions"), x="contributions", y="city", orientation="h", title="城市贡献 Top 20", labels={"contributions": "贡献数", "city": "城市"}, color_discrete_sequence=[COLORS[1]]))


def make_project_country_heatmap(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return empty_figure()
    repo_order = df.groupby("repo")["contributions"].sum().sort_values(ascending=False).head(80).index
    country_order = df.groupby("country")["contributions"].sum().sort_values(ascending=False).head(30).index
    work = df[df["repo"].isin(repo_order) & df["country"].isin(country_order)]
    pivot = work.pivot_table(index="repo", columns="country", values="contributions", aggfunc="sum", fill_value=0)
    return finish(px.imshow(pivot, aspect="auto", title="项目-国家贡献热力图", color_continuous_scale="Blues"))


def make_cluster_scatter(df: pd.DataFrame) -> go.Figure:
    if df.empty or not {"pca_x", "pca_y", "cluster"}.issubset(df.columns):
        return empty_figure("请先生成 ml_results.csv")
    df = _sample(df, n=400)
    return finish(px.scatter(df, x="pca_x", y="pca_y", color="cluster", hover_name="repo", size="stars", title="K-Means 聚类结果", labels={"pca_x": "PCA 1", "pca_y": "PCA 2", "cluster": "聚类", "stars": "Stars"}, color_discrete_sequence=COLORS))


def make_cluster_radar(df: pd.DataFrame) -> go.Figure:
    if df.empty or "cluster" not in df.columns:
        return empty_figure("请先生成 ml_results.csv")
    avg = df.groupby("cluster")[["popularity_score", "activity_score", "health_score", "globalization_score"]].mean().reset_index()
    return make_multi_project_radar(avg.rename(columns={"cluster": "repo"}))


def make_cluster_average_heatmap(df: pd.DataFrame) -> go.Figure:
    cols = ["popularity_score", "activity_score", "health_score", "globalization_score"]
    if df.empty or "cluster" not in df.columns or not set(cols).issubset(df.columns):
        return empty_figure("请先生成 ml_results.csv")
    avg = df.groupby("cluster")[cols].mean(numeric_only=True).round(4)
    avg.index = [f"Cluster {value}" for value in avg.index]
    avg.columns = ["热度", "活跃", "健康", "国际化"]
    fig = px.imshow(
        avg,
        zmin=0,
        zmax=1,
        text_auto=".2f",
        aspect="auto",
        title="聚类平均指标热力图",
        labels={"x": "指标", "y": "聚类", "color": "平均评分"},
        color_continuous_scale="Blues",
    )
    return finish(fig, height=420)


def make_cluster_profile_bar(df: pd.DataFrame) -> go.Figure:
    if df.empty or "cluster" not in df.columns:
        return empty_figure("请先运行 scripts/train_models.py 生成聚类解释")
    cols = [
        col
        for col in ["avg_popularity_score", "avg_activity_score", "avg_health_score", "avg_globalization_score"]
        if col in df.columns
    ]
    if not cols:
        return empty_figure("聚类解释缺少均值评分字段")
    names = {
        "avg_popularity_score": "热度",
        "avg_activity_score": "活跃",
        "avg_health_score": "健康",
        "avg_globalization_score": "国际化",
    }
    long_df = df[["cluster"] + cols].copy()
    for col in cols:
        long_df[col] = pd.to_numeric(long_df[col], errors="coerce").fillna(0)
    long_df["cluster"] = long_df["cluster"].astype(str).map(lambda value: f"Cluster {value}")
    long_df = long_df.melt(id_vars="cluster", value_vars=cols, var_name="评分维度", value_name="平均评分")
    long_df["评分维度"] = long_df["评分维度"].map(names)
    fig = px.bar(
        long_df,
        x="cluster",
        y="平均评分",
        color="评分维度",
        barmode="group",
        title="聚类画像评分对比",
        color_discrete_sequence=COLORS,
    )
    fig.update_yaxes(range=[0, 1])
    return finish(fig, height=430)


def make_anomaly_scatter(df: pd.DataFrame) -> go.Figure:
    if df.empty or not {"pca_x", "pca_y", "anomaly_label"}.issubset(df.columns):
        return empty_figure("请先生成 ml_results.csv")
    df = _sample(df, n=400)
    return finish(px.scatter(df, x="pca_x", y="pca_y", color="anomaly_label", hover_name="repo", size="health_score", title="Isolation Forest 异常检测", labels={"pca_x": "PCA 1", "pca_y": "PCA 2", "anomaly_label": "异常标签", "health_score": "健康度"}, color_discrete_map={"normal": COLORS[3], "anomaly": COLORS[5]}))


def make_risk_project_bar(df: pd.DataFrame) -> go.Figure:
    if df.empty or "repo" not in df.columns or "health_score" not in df.columns:
        return empty_figure("请先生成 ml_results.csv")
    work = df.copy()
    work["health_score"] = pd.to_numeric(work["health_score"], errors="coerce").fillna(0)
    work["activity_score"] = pd.to_numeric(work.get("activity_score", 0), errors="coerce").fillna(0)
    work["popularity_score"] = pd.to_numeric(work.get("popularity_score", 0), errors="coerce").fillna(0)
    work["risk_score"] = (1 - work["health_score"]).clip(0, 1)
    top = work.sort_values(["health_score", "activity_score"], ascending=[True, True]).head(15).copy()
    plot_df = top.sort_values("risk_score", ascending=False)
    fig = px.bar(
        plot_df,
        x="risk_score",
        y="repo",
        orientation="h",
        color="health_score",
        color_continuous_scale="Reds_r",
        title="风险项目健康度排行",
        labels={"risk_score": "风险评分（1 - 健康度）", "repo": "项目", "health_score": "健康度"},
        hover_data=[col for col in ["anomaly_label", "activity_score", "popularity_score", "globalization_score"] if col in top.columns],
        text="health_score",
    )
    fig.update_traces(texttemplate="%{text:.2f}", textposition="outside", cliponaxis=False)
    fig.update_yaxes(categoryorder="array", categoryarray=plot_df["repo"].tolist(), autorange="reversed")
    return finish(fig, height=520)


def make_text_embedding_scatter(df: pd.DataFrame) -> go.Figure:
    if df.empty or not {"text_x", "text_y"}.issubset(df.columns):
        return empty_figure("请先生成 text_results.csv")
    df = _sample(df, n=400)
    return finish(px.scatter(df, x="text_x", y="text_y", color="main_topic", hover_name="repo", title="README 语义嵌入分布", labels={"text_x": "语义维度 1", "text_y": "语义维度 2", "main_topic": "主题"}, color_discrete_sequence=COLORS))


def make_similarity_heatmap(df_or_embeddings: pd.DataFrame, similarity_df: pd.DataFrame | None = None) -> go.Figure:
    df = df_or_embeddings
    if similarity_df is not None and not similarity_df.empty and {"repo_a", "repo_b", "similarity"}.issubset(similarity_df.columns):
        repos = [str(repo) for repo in df.get("repo", pd.Series(dtype=str)).head(80).tolist()] if not df.empty else []
        if not repos:
            repos = list(dict.fromkeys(similarity_df["repo_a"].astype(str).head(80).tolist()))
        work = similarity_df[
            similarity_df["repo_a"].astype(str).isin(repos) & similarity_df["repo_b"].astype(str).isin(repos)
        ].copy()
        if work.empty:
            return empty_figure("暂无文本相似度矩阵")
        work["similarity"] = pd.to_numeric(work["similarity"], errors="coerce").fillna(0)
        pivot = work.pivot_table(index="repo_a", columns="repo_b", values="similarity", aggfunc="mean", fill_value=0)
        pivot = pivot.reindex(index=repos, columns=repos).fillna(0)
        fig = px.imshow(
            pivot,
            zmin=0,
            zmax=1,
            title="项目文本相似度热力图（高维向量余弦相似度）",
            labels={"x": "项目", "y": "项目", "color": "余弦相似度"},
            color_continuous_scale="Blues",
        )
    else:
        if df.empty or not {"text_x", "text_y", "repo"}.issubset(df.columns):
            return empty_figure("请先生成 text_results.csv 或 text_similarity.csv")
        if len(df) > 80:
            df = _sample(df, n=80)
        coords = df[["text_x", "text_y"]].apply(pd.to_numeric, errors="coerce").fillna(0).to_numpy()
        dist = ((coords[:, None, :] - coords[None, :, :]) ** 2).sum(axis=2) ** 0.5
        sim = 1 / (1 + dist)
        fig = px.imshow(
            sim,
            x=df["repo"],
            y=df["repo"],
            title="项目文本相似度热力图（二维坐标近似）",
            labels={"x": "项目", "y": "项目", "color": "近似相似度"},
            color_continuous_scale="Blues",
        )
    fig.update_xaxes(tickangle=45, tickfont=dict(size=10))
    fig.update_yaxes(tickfont=dict(size=10))
    return finish(fig, height=640)


def make_issue_topic_bar(df: pd.DataFrame) -> go.Figure:
    if df.empty or "issue_type" not in df.columns:
        return empty_figure()
    counts = df["issue_type"].value_counts().reset_index()
    counts.columns = ["issue_type", "count"]
    return finish(px.bar(counts, x="issue_type", y="count", title="Issue 主题分布"))


def make_commit_type_bar(df: pd.DataFrame) -> go.Figure:
    if df.empty or "commit_type" not in df.columns:
        return empty_figure()
    counts = df["commit_type"].value_counts().reset_index()
    counts.columns = ["commit_type", "count"]
    return finish(px.bar(counts, x="commit_type", y="count", title="Commit 类型分布"))


TREND_METRICS = {
    "Stars": "stars",
    "Forks": "forks",
    "Open Issues": "open_issues",
}


def _trend_metric_column(metric_label: str) -> str:
    return TREND_METRICS.get(metric_label, "stars")


def _prepare_history(history: pd.DataFrame, metric_label: str = "Stars") -> tuple[pd.DataFrame, str]:
    col = _trend_metric_column(metric_label)
    if history.empty or not {"repo", "collected_at", col}.issubset(history.columns):
        return pd.DataFrame(), col
    work = history.copy()
    work["repo"] = work["repo"].astype(str)
    work["collected_at"] = pd.to_datetime(work["collected_at"], errors="coerce", utc=True)
    work[col] = pd.to_numeric(work[col], errors="coerce").fillna(0)
    work = work.dropna(subset=["collected_at"]).sort_values(["repo", "collected_at"])
    return work, col


def _nonzero_change_summary(work: pd.DataFrame, col: str) -> pd.DataFrame:
    summary = []
    for repo, group in work.groupby("repo"):
        if group.empty:
            continue
        change = float(group.iloc[-1][col]) - float(group.iloc[0][col])
        if change != 0:
            summary.append({"repo": str(repo), "change": change, "latest": float(group.iloc[-1][col])})
    if not summary:
        return pd.DataFrame(columns=["repo", "change", "latest"])
    return pd.DataFrame(summary).sort_values(["change", "latest"], ascending=False)


def make_time_series_line(history: pd.DataFrame, repos: list[str] | None = None, metric_label: str = "Stars") -> go.Figure:
    work, col = _prepare_history(history, metric_label)
    if work.empty:
        return empty_figure("暂无 star_history.csv 时间序列数据")
    selected = [repo for repo in (repos or []) if repo]
    summary = _nonzero_change_summary(work, col)
    if not selected:
        selected = summary.head(6)["repo"].tolist()
    else:
        changed_repos = set(summary[summary["repo"].isin(selected)]["repo"].tolist())
        selected = [repo for repo in selected if repo in changed_repos]
    work = work[work["repo"].isin(selected)]
    if work.empty:
        return empty_figure("所选项目在当前快照范围内没有非 0 变化")
    work = work.sort_values(["repo", "collected_at"]).copy()
    work["snapshot_index"] = work.groupby("repo").cumcount() + 1
    work["_baseline_value"] = work.groupby("repo")[col].transform("first")
    work["change_from_first"] = work[col] - work["_baseline_value"]
    fig = px.line(
        work,
        x="snapshot_index",
        y="change_from_first",
        color="repo",
        markers=True,
        title=f"{metric_label} 历史快照累计变化趋势",
        labels={"snapshot_index": "快照序号", "change_from_first": f"{metric_label} 累计变化量", "repo": "项目"},
        hover_data={
            "snapshot_index": True,
            "change_from_first": ":,.0f",
            col: ":,.0f",
            "collected_at": True,
            "_baseline_value": False,
        },
        color_discrete_sequence=COLORS,
    )
    fig.update_xaxes(dtick=1, tickmode="linear", title="快照序号（第 N 次采集）")
    fig.update_yaxes(title=f"相对首个快照的 {metric_label} 变化量")
    return finish(fig, height=470)


def make_time_series_change_bar(history: pd.DataFrame, repos: list[str] | None = None, metric_label: str = "Stars") -> go.Figure:
    work, col = _prepare_history(history, metric_label)
    if work.empty:
        return empty_figure("暂无时间序列变化数据")
    selected = [repo for repo in (repos or []) if repo]
    if selected:
        work = work[work["repo"].isin(selected)]
    summary = _nonzero_change_summary(work, col)
    if summary.empty:
        return empty_figure("当前快照范围内没有非 0 变化")
    df = summary.head(20)
    fig = px.bar(
        df,
        x="change",
        y="repo",
        orientation="h",
        color="change",
        color_continuous_scale="Tealgrn",
        title=f"{metric_label} 历史快照变化 Top 20",
        labels={"change": "变化量", "repo": "项目"},
        text="change",
    )
    fig.update_traces(texttemplate="%{text:,.0f}", textposition="outside", cliponaxis=False)
    fig.update_yaxes(categoryorder="array", categoryarray=df["repo"].tolist(), autorange="reversed")
    return finish(fig, height=500)


def make_snapshot_coverage_bar(history: pd.DataFrame) -> go.Figure:
    if history.empty or "repo" not in history.columns:
        return empty_figure("暂无采集快照覆盖数据")
    counts = history.groupby("repo").size().reset_index(name="snapshot_count").sort_values("snapshot_count", ascending=False).head(30)
    fig = px.bar(
        counts,
        x="snapshot_count",
        y="repo",
        orientation="h",
        title="项目历史快照覆盖 Top 30",
        labels={"snapshot_count": "快照数", "repo": "项目"},
        color="snapshot_count",
        color_continuous_scale="Blues",
    )
    fig.update_yaxes(categoryorder="array", categoryarray=counts["repo"].tolist(), autorange="reversed")
    return finish(fig, height=560)


def make_star_growth_bar(df: pd.DataFrame, window: str = "30m") -> go.Figure:
    value_col = "growth_30m" if window == "30m" else "growth_24h"
    window_col = "window_30m_available" if window == "30m" else "window_24h_available"
    title = "30 分钟 Stars 增长 Top 20" if window == "30m" else "24 小时 Stars 增长 Top 20"
    if df.empty or value_col not in df.columns:
        return empty_figure("请先运行 scripts/build_star_growth.py")
    work = df.copy()
    work[value_col] = pd.to_numeric(work[value_col], errors="coerce").fillna(0)
    top = work.sort_values(value_col, ascending=False).head(20).copy()
    display_col = value_col
    has_window = True
    if window_col in top.columns:
        has_window = top[window_col].astype(str).str.lower().isin(["true", "1", "yes"]).any()
    if not has_window:
        title = f"{title}（缺少完整窗口快照）"
    if top[value_col].max() <= 0:
        display_col = "_display_growth"
        top[display_col] = 1
        title = f"{title}（当前窗口新增均为 0）"
    hover_cols = [col for col in ["stars_latest", "collected_at", "snapshot_count", "note"] if col in top.columns]
    fig = px.bar(
        top,
        x=display_col,
        y="repo",
        orientation="h",
        title=title,
        labels={display_col: "Stars 增长数", "repo": "项目"},
        color=value_col,
        color_continuous_scale="Blues",
        hover_data=hover_cols,
        text=value_col,
    )
    fig.update_traces(texttemplate="%{text}", textposition="outside", cliponaxis=False)
    if display_col != value_col:
        fig.update_xaxes(showticklabels=False, title="实际增长均为 0，条带仅用于占位显示")
    elif not has_window:
        fig.update_xaxes(title="现有历史快照跨度内 Stars 增长")
    fig.update_yaxes(categoryorder="array", categoryarray=top["repo"].tolist(), autorange="reversed")
    return finish(fig, height=460)


def make_trending_star_bar(df: pd.DataFrame) -> go.Figure:
    if df.empty or "stars" not in df.columns:
        return empty_figure("点击按钮采集 GitHub Trending")
    work = df.copy()
    work["stars"] = pd.to_numeric(work["stars"], errors="coerce").fillna(0)
    top = work.sort_values("stars", ascending=False).head(20)
    fig = px.bar(
        top,
        x="stars",
        y="repo",
        orientation="h",
        color="language" if "language" in top.columns else None,
        title="GitHub Trending Stars 排行",
        labels={"stars": "Stars", "repo": "仓库", "language": "语言"},
        hover_data=[col for col in ["forks", "period_stars", "url"] if col in top.columns],
        color_discrete_sequence=COLORS,
    )
    fig.update_yaxes(categoryorder="array", categoryarray=top["repo"].tolist(), autorange="reversed")
    return finish(fig, height=520)


def make_trending_language_bar(df: pd.DataFrame) -> go.Figure:
    if df.empty or "language" not in df.columns:
        return empty_figure("点击按钮采集 GitHub Trending")
    work = df.copy()
    work["language"] = work["language"].fillna("Unknown").replace("", "Unknown")
    counts = work["language"].value_counts().reset_index()
    counts.columns = ["language", "count"]
    fig = px.bar(
        counts,
        x="language",
        y="count",
        color="language",
        title="Trending 语言分布",
        labels={"language": "语言", "count": "仓库数"},
        color_discrete_sequence=COLORS,
    )
    return finish(fig, height=360)


def _repo_label_margin(labels: pd.Series, min_margin: int = 210, max_margin: int = 360) -> int:
    if labels.empty:
        return min_margin
    max_length = labels.fillna("").astype(str).map(len).max()
    return min(max_margin, max(min_margin, int(max_length * 7.2) + 56))


def _horizontal_bar_height(count: int, min_height: int = 560, row_height: int = 27, extra: int = 170) -> int:
    return max(min_height, count * row_height + extra)


def make_star_rank_bar(df: pd.DataFrame) -> go.Figure:
    if df.empty or "stars" not in df.columns:
        return empty_figure("点击按钮查询 GitHub Stars 实时榜")
    work = df.copy()
    work["stars"] = pd.to_numeric(work["stars"], errors="coerce").fillna(0)
    top = work.sort_values("stars", ascending=False).head(30)
    fig = px.bar(
        top,
        x="stars",
        y="repo",
        orientation="h",
        color="language" if "language" in top.columns else None,
        title="GitHub Stars 实时排行",
        labels={"stars": "Stars", "repo": "仓库", "language": "语言"},
        hover_data=[col for col in ["forks", "open_issues", "url", "updated_at"] if col in top.columns],
        color_discrete_sequence=COLORS,
    )
    repo_labels = top["repo"].astype(str).tolist()
    fig.update_yaxes(
        categoryorder="array",
        categoryarray=repo_labels,
        autorange="reversed",
        tickmode="array",
        tickvals=repo_labels,
        ticktext=repo_labels,
        tickfont=dict(size=12),
    )
    fig = finish(fig, height=_horizontal_bar_height(len(top)))
    fig.update_layout(
        margin=dict(
            l=_repo_label_margin(top["repo"]),
            r=40,
            t=35,
            b=fig.layout.margin.b if fig.layout.margin and fig.layout.margin.b is not None else 105,
        )
    )
    fig.update_yaxes(automargin=True)
    return fig


def make_star_rank_language_bar(df: pd.DataFrame) -> go.Figure:
    if df.empty or "language" not in df.columns:
        return empty_figure("点击按钮查询 GitHub Stars 实时榜")
    work = df.copy()
    work["language"] = work["language"].fillna("Unknown").replace("", "Unknown")
    counts = work["language"].value_counts().reset_index()
    counts.columns = ["language", "count"]
    fig = px.bar(
        counts,
        x="language",
        y="count",
        color="language",
        title="Stars 榜语言分布",
        labels={"language": "语言", "count": "仓库数"},
        color_discrete_sequence=COLORS,
    )
    return finish(fig, height=360)
