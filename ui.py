from __future__ import annotations

import html

import streamlit as st


LIGHT = {
    "bg": "#f6f7fb",
    "surface": "#ffffff",
    "surface2": "#f9fafc",
    "text": "#111827",
    "muted": "#667085",
    "border": "#e7e9ee",
    "accent": "#625bf6",
    "accent2": "#7c3aed",
    "success": "#12b76a",
}

DARK = {
    "bg": "#0b0d12",
    "surface": "#11141b",
    "surface2": "#171a22",
    "text": "#f4f4f5",
    "muted": "#a1a1aa",
    "border": "#272a34",
    "accent": "#8b83ff",
    "accent2": "#a78bfa",
    "success": "#32d583",
}


def inject_css(dark: bool = False) -> None:
    t = DARK if dark else LIGHT
    st.markdown(
        f"""
        <style>
        :root {{
            --app-bg:{t['bg']}; --app-surface:{t['surface']}; --app-surface-2:{t['surface2']};
            --app-text:{t['text']}; --app-muted:{t['muted']}; --app-border:{t['border']};
            --app-accent:{t['accent']}; --app-accent-2:{t['accent2']}; --app-success:{t['success']};
        }}
        .stApp {{ background: var(--app-bg); color: var(--app-text); }}
        .block-container {{ max-width: 1440px; padding-top: 1.15rem; padding-bottom: 4rem; }}
        [data-testid="stSidebar"] {{ background: var(--app-surface); border-right: 1px solid var(--app-border); }}
        [data-testid="stSidebar"] * {{ color: var(--app-text); }}
        h1,h2,h3,h4,p,span,label,div {{ letter-spacing: -0.01em; }}
        h1 {{ letter-spacing: -0.045em !important; font-weight: 760 !important; }}
        h2,h3 {{ letter-spacing: -0.025em !important; }}
        [data-testid="stHeader"] {{ background: transparent; }}
        [data-testid="stToolbar"] {{ right: 1rem; }}

        .hero {{
            position: relative; overflow: hidden; border: 1px solid var(--app-border);
            background: linear-gradient(135deg, var(--app-surface) 0%, var(--app-surface-2) 100%);
            border-radius: 24px; padding: 28px 30px; margin: 8px 0 20px;
        }}
        .hero:after {{
            content:""; position:absolute; width:240px; height:240px; right:-80px; top:-110px;
            border-radius:50%; background: radial-gradient(circle, rgba(98,91,246,.20), rgba(98,91,246,0) 70%);
            pointer-events:none;
        }}
        .eyebrow {{ display:inline-flex; align-items:center; gap:8px; font-size:.78rem; font-weight:700;
            color:var(--app-accent); text-transform:uppercase; letter-spacing:.08em; margin-bottom:10px; }}
        .hero-title {{ font-size: clamp(1.8rem, 3vw, 3rem); line-height:1.04; font-weight:780; color:var(--app-text); max-width:850px; letter-spacing:-.045em; }}
        .hero-copy {{ margin-top:12px; color:var(--app-muted); font-size:1rem; line-height:1.65; max-width:900px; }}
        .hero-chip {{ display:inline-flex; margin:16px 7px 0 0; padding:7px 10px; border:1px solid var(--app-border);
            border-radius:999px; color:var(--app-muted); background:var(--app-surface); font-size:.78rem; }}

        .metric-card {{ border:1px solid var(--app-border); background:var(--app-surface); border-radius:18px;
            padding:17px 18px; min-height:104px; }}
        .metric-label {{ color:var(--app-muted); font-size:.78rem; font-weight:650; margin-bottom:9px; }}
        .metric-value {{ color:var(--app-text); font-size:1.7rem; font-weight:760; letter-spacing:-.04em; line-height:1; }}
        .metric-sub {{ color:var(--app-muted); font-size:.72rem; margin-top:8px; }}

        .section-card {{ border:1px solid var(--app-border); background:var(--app-surface); border-radius:20px; padding:20px; margin-bottom:14px; }}
        .section-kicker {{ color:var(--app-accent); font-size:.76rem; font-weight:750; text-transform:uppercase; letter-spacing:.075em; }}
        .section-title {{ color:var(--app-text); font-size:1.25rem; font-weight:720; margin:3px 0 3px; }}
        .section-copy {{ color:var(--app-muted); font-size:.88rem; line-height:1.55; }}

        .relation-pill {{ display:inline-flex; align-items:center; gap:8px; padding:9px 12px; margin:4px 6px 4px 0;
            background:var(--app-surface-2); border:1px solid var(--app-border); border-radius:12px; color:var(--app-text); font-size:.84rem; }}
        .relation-pill b {{ color:var(--app-accent); }}
        .status-dot {{ width:7px; height:7px; border-radius:50%; display:inline-block; background:var(--app-success); margin-right:6px; }}
        .small-muted {{ color:var(--app-muted); font-size:.8rem; }}

        div[data-testid="stDataFrame"] {{ border:1px solid var(--app-border); border-radius:14px; overflow:hidden; }}
        div[data-testid="stMetric"] {{ background:var(--app-surface); border:1px solid var(--app-border); border-radius:16px; padding:12px; }}
        div[data-baseweb="select"] > div, textarea, input {{ border-radius:12px !important; }}
        [data-testid="stTextArea"] textarea {{ background:var(--app-surface) !important; border-color:var(--app-border) !important; color:var(--app-text) !important; line-height:1.55; }}
        .stButton > button, .stDownloadButton > button {{ border-radius:12px; min-height:42px; font-weight:650; }}
        .stButton > button[kind="primary"] {{ background:linear-gradient(135deg,var(--app-accent),var(--app-accent-2)); border:0; }}
        [data-testid="stForm"] {{ border:0; padding:0; }}
        [data-testid="stTabs"] [role="tablist"] {{ gap:7px; overflow-x:auto; padding-bottom:4px; }}
        [data-testid="stTabs"] button[role="tab"] {{ border:1px solid var(--app-border); border-radius:11px; background:var(--app-surface); padding:8px 13px; }}
        [data-testid="stTabs"] button[aria-selected="true"] {{ border-color:var(--app-accent); color:var(--app-accent); }}
        hr {{ border-color:var(--app-border) !important; }}
        @media (max-width: 760px) {{
            .block-container {{ padding-left:1rem; padding-right:1rem; }}
            .hero {{ padding:22px 19px; border-radius:19px; }}
            .hero-title {{ font-size:1.85rem; }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def hero() -> None:
    st.markdown(
        """
        <section class="hero">
          <div class="eyebrow">◉ Linguistic intelligence workspace</div>
          <div class="hero-title">Understand the structure behind any English text.</div>
          <div class="hero-copy">Explore entities and relationships, syntax, word classes, lemmas, stems, morphology and dependency structure from one production-ready NLP workspace.</div>
          <div>
            <span class="hero-chip">spaCy pipeline</span>
            <span class="hero-chip">NLTK stemming</span>
            <span class="hero-chip">Interactive Plotly views</span>
            <span class="hero-chip">Dependency graph</span>
          </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def metric_card(label: str, value: str | int, sub: str) -> None:
    st.markdown(
        f"""
        <div class="metric-card">
          <div class="metric-label">{html.escape(label)}</div>
          <div class="metric-value">{html.escape(str(value))}</div>
          <div class="metric-sub">{html.escape(sub)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_header(kicker: str, title: str, copy: str) -> None:
    st.markdown(
        f"""
        <div style="margin:4px 0 14px">
          <div class="section-kicker">{html.escape(kicker)}</div>
          <div class="section-title">{html.escape(title)}</div>
          <div class="section-copy">{html.escape(copy)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def relation_pills(rows) -> None:
    if rows.empty:
        return
    markup = []
    for _, row in rows.head(8).iterrows():
        markup.append(
            '<span class="relation-pill">'
            f'<span>{html.escape(str(row["Subject"]))}</span>'
            f'<b>→ {html.escape(str(row["Relation"]))} →</b>'
            f'<span>{html.escape(str(row["Object"]))}</span>'
            '</span>'
        )
    st.markdown("".join(markup), unsafe_allow_html=True)
