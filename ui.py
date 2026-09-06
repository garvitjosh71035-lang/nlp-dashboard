from __future__ import annotations

import html
import streamlit as st


TASKS = [
    ("Named-Entity Relationship", "Entities and subject → relation → object links", "NER"),
    ("POS Tagging", "Part-of-speech details for every token", "POS"),
    ("POS Distribution", "See how grammatical categories are distributed", "DIST"),
    ("Lemmatization", "Convert words to their dictionary forms", "LEMMA"),
    ("Stemming", "Reduce words with Porter stemming", "STEM"),
    ("Morphology", "Inspect tense, number, person and more", "MORPH"),
    ("Dependencies", "Visualize syntax with displaCy style=dep", "DEP"),
]


def inject_css():
    st.markdown(
        """
<style>
:root {
  --app-max: 1080px;
}

.block-container {
  max-width: var(--app-max);
  padding-top: 1.2rem;
  padding-bottom: 3rem;
}

[data-testid="stHeader"] { background: rgba(255,255,255,0); }

.app-kicker {
  font-size: .78rem;
  font-weight: 700;
  letter-spacing: .11em;
  text-transform: uppercase;
  opacity: .65;
  margin-bottom: .35rem;
}

.app-title {
  font-size: clamp(2rem, 5vw, 3.35rem);
  line-height: 1.02;
  font-weight: 800;
  letter-spacing: -.045em;
  margin: 0;
}

.app-subtitle {
  font-size: clamp(1rem, 2.2vw, 1.15rem);
  opacity: .72;
  max-width: 720px;
  margin-top: .8rem;
  margin-bottom: 1.1rem;
}

.status-pill {
  display: inline-flex;
  align-items: center;
  gap: .45rem;
  border: 1px solid rgba(128,128,128,.28);
  border-radius: 999px;
  padding: .38rem .7rem;
  font-size: .82rem;
  margin: .2rem .35rem .2rem 0;
}

.section-label {
  font-size: .82rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: .08em;
  opacity: .58;
  margin: 1.4rem 0 .45rem;
}

.task-help {
  opacity: .64;
  font-size: .9rem;
  margin-top: -.2rem;
  margin-bottom: .9rem;
}

.result-title {
  font-size: clamp(1.45rem, 3.5vw, 2rem);
  font-weight: 800;
  letter-spacing: -.025em;
  margin: .2rem 0 .2rem;
}

.metric-card {
  border: 1px solid rgba(128,128,128,.22);
  border-radius: 16px;
  padding: .85rem .9rem;
  min-height: 86px;
}
.metric-card .metric-label { font-size:.78rem; opacity:.62; }
.metric-card .metric-value { font-size:1.45rem; font-weight:800; margin-top:.18rem; }

.relation-card {
  border: 1px solid rgba(128,128,128,.22);
  border-radius: 14px;
  padding: .9rem;
  margin: .55rem 0;
  line-height: 1.55;
}
.relation-arrow { opacity:.62; padding:0 .3rem; }
.relation-word { font-weight:800; }

.entity-chip {
  display:inline-flex;
  gap:.4rem;
  align-items:center;
  border:1px solid rgba(128,128,128,.24);
  border-radius:999px;
  padding:.35rem .6rem;
  margin:.18rem .2rem .18rem 0;
  font-size:.86rem;
}
.entity-chip small { opacity:.58; }

div.stButton > button {
  min-height: 48px;
  border-radius: 12px;
  font-weight: 700;
  width: 100%;
}

[data-testid="stTextArea"] textarea {
  min-height: 155px;
  border-radius: 14px;
  font-size: 16px;
}

[data-testid="stFileUploader"] {
  border-radius: 14px;
}

[data-testid="stDataFrame"] { border-radius: 14px; overflow: hidden; }

.dep-scroll {
  overflow-x: auto;
  padding: .75rem .25rem;
  border: 1px solid rgba(128,128,128,.2);
  border-radius: 14px;
}
.dep-scroll svg { min-width: 720px; }

.mobile-note {
  opacity:.6;
  font-size:.82rem;
  margin-top:.45rem;
}

@media (max-width: 700px) {
  .block-container { padding-left: .9rem; padding-right: .9rem; padding-top:.7rem; }
  [data-testid="stHorizontalBlock"] { flex-wrap: wrap !important; gap: .45rem !important; }
  [data-testid="column"] { flex: 1 1 100% !important; width: 100% !important; min-width: 0 !important; }
  .metric-card { min-height:72px; padding:.7rem .75rem; }
  .app-subtitle { margin-bottom:.7rem; }
  div.stButton > button { min-height: 52px; }
}
</style>
        """,
        unsafe_allow_html=True,
    )


def hero():
    st.markdown('<div class="app-kicker">NLP Analysis Workspace</div>', unsafe_allow_html=True)
    st.markdown('<h1 class="app-title">Text analysis without the clutter.</h1>', unsafe_allow_html=True)
    st.markdown(
        '<div class="app-subtitle">Paste text once, analyze it, then open exactly the NLP operation you need. The interface is designed to stay simple on desktop and mobile.</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<span class="status-pill">● spaCy pipeline</span><span class="status-pill">● NLTK stemming</span><span class="status-pill">● Mobile ready</span>',
        unsafe_allow_html=True,
    )


def metric_cards(summary: dict[str, int]):
    items = [
        ("Words", summary.get("words", 0)),
        ("Sentences", summary.get("sentences", 0)),
        ("Entities", summary.get("entities", 0)),
        ("Relations", summary.get("relationships", 0)),
    ]
    cols = st.columns(4)
    for col, (label, value) in zip(cols, items):
        with col:
            st.markdown(
                f'<div class="metric-card"><div class="metric-label">{html.escape(label)}</div><div class="metric-value">{value}</div></div>',
                unsafe_allow_html=True,
            )


def task_buttons(active_task: str | None, disabled: bool) -> str | None:
    st.markdown('<div class="section-label">Choose an operation</div>', unsafe_allow_html=True)
    selected = active_task

    # Two rows on desktop. CSS turns every column into a full-width row on phones.
    rows = [TASKS[:4], TASKS[4:]]
    for row in rows:
        cols = st.columns(len(row))
        for col, (label, help_text, key) in zip(cols, row):
            with col:
                button_label = f"✓ {label}" if active_task == key else label
                if st.button(button_label, key=f"task_{key}", use_container_width=True, disabled=disabled):
                    selected = key
                st.caption(help_text)
    return selected


def result_header(title: str, description: str):
    st.divider()
    st.markdown(f'<div class="result-title">{html.escape(title)}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="task-help">{html.escape(description)}</div>', unsafe_allow_html=True)
