from __future__ import annotations

import html
import json
from io import BytesIO
from zipfile import ZIP_DEFLATED, ZipFile

import pandas as pd
import plotly.express as px
import streamlit as st

from nlp_engine import AnalysisResult, analyze_text, load_model
from ui import TASKS, hero, inject_css, metric_cards, result_header, task_buttons


MAX_CHARS = 15_000
SAMPLE_TEXT = (
    "Microsoft acquired GitHub in 2018. Satya Nadella leads Microsoft, "
    "and the company partners with OpenAI on artificial intelligence research."
)


st.set_page_config(
    page_title="NLP Dashboard",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

inject_css()
hero()


@st.cache_resource(show_spinner=False)
def get_nlp():
    return load_model()


@st.cache_data(show_spinner=False, max_entries=32)
def cached_analysis(text: str) -> AnalysisResult:
    return analyze_text(text, get_nlp())


def _csv_bytes(rows):
    return pd.DataFrame(rows).to_csv(index=False).encode("utf-8")


def _analysis_zip(result: AnalysisResult) -> bytes:
    buffer = BytesIO()
    with ZipFile(buffer, "w", ZIP_DEFLATED) as zf:
        zf.writestr("source.txt", result.text)
        zf.writestr("summary.json", json.dumps(result.summary, indent=2))
        zf.writestr("entities.csv", _csv_bytes(result.entities))
        zf.writestr("relationships.csv", _csv_bytes(result.relationships))
        zf.writestr("pos_tagging.csv", _csv_bytes(result.pos))
        zf.writestr("pos_distribution.csv", _csv_bytes(result.pos_distribution))
        zf.writestr("lemmatization.csv", _csv_bytes(result.lemmas))
        zf.writestr("stemming.csv", _csv_bytes(result.stems))
        morph_flat = [
            {
                "Token": row["Token"],
                "POS": row["POS"],
                "Morphology": row["Morphology"],
                **row["Features"],
            }
            for row in result.morphology
        ]
        zf.writestr("morphology.csv", _csv_bytes(morph_flat))
    return buffer.getvalue()


def _use_sample():
    st.session_state.source_text = SAMPLE_TEXT
    st.session_state.analysis = None
    st.session_state.analyzed_text = ""
    st.session_state.active_task = None


def _start_over():
    st.session_state.source_text = ""
    st.session_state.analysis = None
    st.session_state.analyzed_text = ""
    st.session_state.active_task = None


def _ensure_state():
    st.session_state.setdefault("source_text", SAMPLE_TEXT)
    st.session_state.setdefault("analysis", None)
    st.session_state.setdefault("analyzed_text", "")
    st.session_state.setdefault("active_task", None)


_ensure_state()

st.markdown('<div class="section-label">1 · Add text</div>', unsafe_allow_html=True)

text = st.text_area(
    "Text to analyze",
    key="source_text",
    placeholder="Paste an English paragraph here…",
    max_chars=MAX_CHARS,
    label_visibility="collapsed",
)

left, right = st.columns([3, 1])
with left:
    analyze_clicked = st.button("Analyze text", type="primary", use_container_width=True)
with right:
    st.button("Use sample", use_container_width=True, on_click=_use_sample)

st.caption(f"{len(text):,}/{MAX_CHARS:,} characters · Analysis runs only when you press Analyze text.")

if analyze_clicked:
    if not text.strip():
        st.warning("Enter some English text first.")
    elif len(text) > MAX_CHARS:
        st.error(f"Please keep the input under {MAX_CHARS:,} characters.")
    else:
        try:
            with st.spinner("Analyzing language structure…"):
                st.session_state.analysis = cached_analysis(text)
                st.session_state.analyzed_text = text
                if st.session_state.active_task is None:
                    st.session_state.active_task = "NER"
        except Exception as exc:
            st.session_state.analysis = None
            st.error("The NLP pipeline could not analyze this text.")
            with st.expander("Technical details"):
                st.code(str(exc))

result: AnalysisResult | None = st.session_state.analysis
is_stale = bool(result) and text != st.session_state.analyzed_text

if result:
    st.markdown('<div class="section-label">2 · Analysis summary</div>', unsafe_allow_html=True)
    metric_cards(result.summary)
    if is_stale:
        st.warning("The text has changed since the last analysis. Press **Analyze text** again before using the results.")

    st.session_state.active_task = task_buttons(st.session_state.active_task, disabled=is_stale)

    export_col, reset_col = st.columns([2, 1])
    with export_col:
        st.download_button(
            "Download all results (.zip)",
            data=_analysis_zip(result),
            file_name="nlp_analysis.zip",
            mime="application/zip",
            use_container_width=True,
            disabled=is_stale,
        )
    with reset_col:
        st.button("Start over", use_container_width=True, on_click=_start_over)

    task = st.session_state.active_task

    if task == "NER" and not is_stale:
        result_header("Named-Entity Relationship", "See recognized entities first, then inspect deterministic subject → relation → object links from the dependency parse.")
        if result.entities:
            st.markdown(result.entity_html, unsafe_allow_html=True)
            st.dataframe(pd.DataFrame(result.entities)[["Text", "Label", "Meaning"]], use_container_width=True, hide_index=True)
            st.download_button("Download entities CSV", _csv_bytes(result.entities), "entities.csv", "text/csv")
        else:
            st.info("No named entities were detected in this text.")

        st.markdown("#### Relationships")
        if result.relationships:
            for row in result.relationships:
                st.markdown(
                    f"<div class='relation-card'><span class='relation-word'>{html.escape(str(row['Subject']))}</span>"
                    f"<span class='relation-arrow'>→</span>{html.escape(str(row['Relation']))}<span class='relation-arrow'>→</span>"
                    f"<span class='relation-word'>{html.escape(str(row['Object']))}</span><br><small>{html.escape(str(row['Sentence']))}</small></div>",
                    unsafe_allow_html=True,
                )
            st.dataframe(pd.DataFrame(result.relationships), use_container_width=True, hide_index=True)
            st.download_button("Download relationships CSV", _csv_bytes(result.relationships), "relationships.csv", "text/csv")
        else:
            st.info("No clear subject–relation–object triple was found. Try a sentence such as “Microsoft acquired GitHub.”")

    elif task == "POS" and not is_stale:
        result_header("POS Tagging", "Inspect each token's part of speech, fine-grained tag, lemma, dependency and syntactic head.")
        df = pd.DataFrame(result.pos)
        choices = ["All"] + sorted(df["POS"].dropna().unique().tolist())
        selected = st.selectbox("Filter by POS", choices)
        shown = df if selected == "All" else df[df["POS"] == selected]
        st.dataframe(shown, use_container_width=True, hide_index=True)
        st.download_button("Download POS tagging CSV", _csv_bytes(result.pos), "pos_tagging.csv", "text/csv")

    elif task == "DIST" and not is_stale:
        result_header("POS Distribution", "Compare how often nouns, verbs, adjectives and other grammatical categories appear.")
        df = pd.DataFrame(result.pos_distribution)
        view = st.radio("Chart", ["Bar", "Donut"], horizontal=True)
        if view == "Bar":
            fig = px.bar(df, x="POS", y="Count", hover_data=["Meaning", "Percent"], text="Count")
        else:
            fig = px.pie(df, names="POS", values="Count", hole=.5, hover_data=["Meaning", "Percent"])
        fig.update_layout(margin=dict(l=8, r=8, t=20, b=8), height=390, legend_title_text="POS")
        st.plotly_chart(fig, use_container_width=True, config={"displaylogo": False, "responsive": True})
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.download_button("Download POS distribution CSV", _csv_bytes(result.pos_distribution), "pos_distribution.csv", "text/csv")

    elif task == "LEMMA" and not is_stale:
        result_header("Lemmatization", "Compare each token with its dictionary/base form.")
        df = pd.DataFrame(result.lemmas)
        changed = int(df["Changed"].sum()) if not df.empty else 0
        st.metric("Forms changed", changed)
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.markdown("**Lemmatized sequence**")
        st.code(" ".join(df["Lemma"].tolist()), wrap_lines=True)
        st.download_button("Download lemmatization CSV", _csv_bytes(result.lemmas), "lemmatization.csv", "text/csv")

    elif task == "STEM" and not is_stale:
        result_header("Stemming", "Use NLTK's Porter Stemmer to reduce tokens to algorithmic stems. Stems are not always valid dictionary words.")
        df = pd.DataFrame(result.stems)
        changed = int(df["Changed"].sum()) if not df.empty else 0
        st.metric("Forms changed", changed)
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.markdown("**Stemmed sequence**")
        st.code(" ".join(df["Stem"].tolist()), wrap_lines=True)
        st.download_button("Download stemming CSV", _csv_bytes(result.stems), "stemming.csv", "text/csv")

    elif task == "MORPH" and not is_stale:
        result_header("Morphology", "Inspect grammatical features such as tense, number, person, degree and verb form.")
        flattened = []
        for row in result.morphology:
            flattened.append({"Token": row["Token"], "POS": row["POS"], "Morphology": row["Morphology"], **row["Features"]})
        df = pd.DataFrame(flattened).fillna("—")
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.download_button("Download morphology CSV", df.to_csv(index=False).encode("utf-8"), "morphology.csv", "text/csv")

    elif task == "DEP" and not is_stale:
        result_header("Dependencies · style=dep", "Choose a sentence and inspect its syntactic dependency arrows using spaCy's displaCy renderer.")
        sentence_labels = [f"{row['index']}. {row['text']}" for row in result.dependency_sentences]
        selected_label = st.selectbox("Sentence", sentence_labels)
        idx = sentence_labels.index(selected_label)
        sentence = result.dependency_sentences[idx]
        st.markdown(f"<div class='dep-scroll'>{sentence['html']}</div>", unsafe_allow_html=True)
        st.caption("On phones, swipe horizontally inside the dependency diagram if the sentence is wide.")
        st.dataframe(pd.DataFrame(sentence["tokens"]), use_container_width=True, hide_index=True)

else:
    st.markdown('<div class="section-label">2 · Pick a task after analysis</div>', unsafe_allow_html=True)
    st.info("Press **Analyze text** first. The seven NLP operations will appear as separate buttons here.")
