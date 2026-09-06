from __future__ import annotations

import math

import pandas as pd
import plotly.graph_objects as go


def configure_figure(fig: go.Figure, *, height: int = 390) -> go.Figure:
    fig.update_layout(
        height=height,
        margin=dict(l=16, r=16, t=38, b=16),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, ui-sans-serif, system-ui"),
        hoverlabel=dict(font_size=13),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
    )
    return fig


def pos_bar_chart(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure(
        go.Bar(
            x=df["POS"],
            y=df["Count"],
            text=df["Count"],
            textposition="outside",
            customdata=df[["Meaning", "Share (%)"]],
            hovertemplate=(
                "<b>%{x}</b><br>%{customdata[0]}<br>Count: %{y}<br>Share: %{customdata[1]}%<extra></extra>"
            ),
            marker=dict(cornerradius=7),
        )
    )
    fig.update_yaxes(title=None, gridcolor="rgba(127,127,127,.12)", zeroline=False)
    fig.update_xaxes(title=None)
    return configure_figure(fig)


def pos_donut_chart(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure(
        go.Pie(
            labels=df["POS"],
            values=df["Count"],
            hole=0.62,
            textinfo="label+percent",
            hovertemplate="<b>%{label}</b><br>Count: %{value}<br>%{percent}<extra></extra>",
        )
    )
    fig.update_layout(showlegend=True)
    return configure_figure(fig)


def relationship_graph(df: pd.DataFrame) -> go.Figure | None:
    if df.empty:
        return None

    labels: list[str] = []
    node_types: dict[str, str] = {}
    for _, row in df.iterrows():
        for label_col, type_col in [("Subject", "Subject type"), ("Object", "Object type")]:
            label = str(row[label_col])
            if label not in labels:
                labels.append(label)
            if label not in node_types or node_types[label] == "—":
                node_types[label] = str(row[type_col])

    n = len(labels)
    positions: dict[str, tuple[float, float]] = {}
    for idx, label in enumerate(labels):
        angle = (2 * math.pi * idx / max(n, 1)) - math.pi / 2
        positions[label] = (math.cos(angle), math.sin(angle))

    edge_x: list[float | None] = []
    edge_y: list[float | None] = []
    annotations = []
    for _, row in df.iterrows():
        source = str(row["Subject"])
        target = str(row["Object"])
        x0, y0 = positions[source]
        x1, y1 = positions[target]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
        annotations.extend(
            [
                dict(
                    x=(x0 + x1) / 2,
                    y=(y0 + y1) / 2,
                    text=str(row["Relation"]),
                    showarrow=False,
                    bgcolor="rgba(255,255,255,.90)",
                    bordercolor="rgba(127,127,127,.18)",
                    borderpad=4,
                    font=dict(size=11, color="#344054"),
                ),
                dict(
                    x=x1, y=y1, ax=x0, ay=y0,
                    xref="x", yref="y", axref="x", ayref="y",
                    text="", showarrow=True, arrowhead=3, arrowsize=1.0,
                    arrowwidth=1.4, arrowcolor="rgba(98,91,246,.55)",
                    standoff=20, startstandoff=20,
                ),
            ]
        )

    edge_trace = go.Scatter(
        x=edge_x,
        y=edge_y,
        mode="lines",
        line=dict(width=1.7, color="rgba(120,120,140,.42)"),
        hoverinfo="skip",
    )

    node_x, node_y, hover, node_text = [], [], [], []
    for label in labels:
        x, y = positions[label]
        node_x.append(x)
        node_y.append(y)
        node_text.append(label if len(label) <= 22 else label[:21] + "…")
        hover.append(f"<b>{label}</b><br>Type: {node_types.get(label, '—')}")

    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode="markers+text",
        text=node_text,
        textposition="bottom center",
        hovertext=hover,
        hoverinfo="text",
        marker=dict(size=34, line=dict(width=2, color="rgba(255,255,255,.9)")),
    )

    fig = go.Figure([edge_trace, node_trace])
    fig.update_layout(
        annotations=annotations,
        xaxis=dict(visible=False, range=[-1.35, 1.35]),
        yaxis=dict(visible=False, range=[-1.35, 1.35], scaleanchor="x", scaleratio=1),
        showlegend=False,
        dragmode="pan",
    )
    return configure_figure(fig, height=470)
