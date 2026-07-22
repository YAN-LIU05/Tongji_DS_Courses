from __future__ import annotations

import reflex as rx


def project_table(rows: list[dict]) -> rx.Component:
    return rx.table.root(
        rx.table.header(
            rx.table.row(
                rx.table.column_header_cell("项目"),
                rx.table.column_header_cell("语言"),
                rx.table.column_header_cell("Stars"),
                rx.table.column_header_cell("热度"),
                rx.table.column_header_cell("活跃"),
                rx.table.column_header_cell("健康"),
            )
        ),
        rx.table.body(
            rx.foreach(
                rows,
                lambda row: rx.table.row(
                    rx.table.cell(row["repo"]),
                    rx.table.cell(row["language"]),
                    rx.table.cell(row["stars"]),
                    rx.table.cell(row["popularity_score"]),
                    rx.table.cell(row["activity_score"]),
                    rx.table.cell(row["health_score"]),
                ),
            )
        ),
        width="100%",
    )

