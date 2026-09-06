from __future__ import annotations

import io
import json
import time
import zipfile

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from spacy import displacy

from nlp_utils import (
    MAX_TEXT_CHARS,
    analysis_summary,
    csv_bytes,
    dependency_rows,
    entity_rows,
    expanded_morphology_rows,
    lemma_rows,
    load_model,
    morphology_rows,
    normalize_input,
    pos_distribution,
    relationship_rows,
    restore_doc,
    sentence_rows,
    serialize_doc,
    stem_rows,
    token_rows,
)
from ui import hero, inject_css, metric_card, relation_pills, section_header
from visualizations import pos_bar_chart, pos_donut_chart, relationship_graph

st.set_page_config(
    page_title="LexiScope · NLP Intelligence",
    page_icon="◉",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "About": "LexiScope is an interactive NLP dashboard built with Streamlit, spaCy, NLTK and Plotly.",
    },
)

SAMPLE_TEXTS = {
    "Technology & AI": (
        "Sundar Pichai leads Google, and the company develops artificial intelligence products in California. "
        "Microsoft invested in OpenAI in 2019, while researchers continue to study generative AI systems."
    ),
    "Business relationship": (
        "Microsoft acquired GitHub in 2018. Satya Nadella leads Microsoft and the company partners with OpenAI."
    ),
    "Travel & places": (
        "Alice travelled from Delhi to Budapest on Monday. She visited the Hungarian Parliament and met "
        "researchers from Eötvös Loránd University."
    ),
    "Grammar showcase": (
        "The curious students carefully analyzed several difficult sentences and presented their findings to the professor."
    ),
}


@st.cache_resource(show_spinner="Loading the English NLP model…")
def get_nlp():
    return load_model()


@st.cache_data(show_spinner=False, max_entries=64)
def cached_doc_bytes(text: str) -> bytes:
    return serialize_doc(get_nlp(), text)


def analyze(text: str):
    payload = cached_doc_bytes(text)
    return restore_doc(get_nlp(), payload)


def export_bundle(text: str, tables: dict[str, pd.DataFrame], summary: dict) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("source.txt", text)
        archive.writestr("summary.json", json.dumps(summary, indent=2))
        for name, frame in tables.items():
            archive.writestr(f"{name}.csv", frame.to_csv(index=False))
    return buffer.getvalue()


def state_init() -> None:
    if "draft_text" not in st.session_state:
        st.session_state.draft_text = SAMPLE_TEXTS["Technology & AI"]
    if "analyzed_text" not in st.session_state:
        st.session_state.analyzed_text = SAMPLE_TEXTS["Technology & AI"]
    if "last_analysis_ms" not in st.session_state:
        st.session_state.last_analysis_ms = None


state_init()
inject_css(False)
nlp = get_nlp()

with st.sidebar:
    st.markdown("### ◉ LexiScope")
    st.caption("Interactive linguistic intelligence")
    st.divider()

    st.markdown("**Workspace**")
    sample = st.selectbox("Example dataset", list(SAMPLE_TEXTS.keys()), label_visibility="collapsed")
    c1, c2 = st.columns(2)
    if c1.button("Use example", use_container_width=True):
        st.session_state.draft_text = SAMPLE_TEXTS[sample]
        st.rerun()
    if c2.button("Clear", use_container_width=True):
        st.session_state.draft_text = ""
        st.rerun()

    uploaded = st.file_uploader("Or import a .txt file", type=["txt"], help=f"Maximum analyzed text: {MAX_TEXT_CHARS:,} characters")
    if uploaded is not None:
        raw = uploaded.getvalue()
        if len(raw) > 100_000:
            st.error("That text file is too large for this demo workspace.")
        else:
            try:
                decoded = raw.decode("utf-8")
                if st.button("Load uploaded text", use_container_width=True):
                    st.session_state.draft_text = decoded[:MAX_TEXT_CHARS]
                    st.rerun()
            except UnicodeDecodeError:
                st.error("Please upload a UTF-8 encoded text file.")

    st.divider()
    st.markdown("**Engine status**")
    st.markdown('<div class="small-muted"><span class="status-dot"></span>spaCy model loaded</div>', unsafe_allow_html=True)
    st.caption("en_core_web_sm · tokenizer · tagger · parser · lemmatizer · NER")
    st.caption("Health monitor: every 30 minutes")

hero()

with st.form("analysis-form", border=False):
    left, right = st.columns([5.2, 1.35], vertical_alignment="bottom")
    with left:
        st.text_area(
            "Text to analyze",
            key="draft_text",
            height=178,
            max_chars=MAX_TEXT_CHARS,
            placeholder="Paste an English paragraph, sentence, report excerpt, or article passage…",
            help="Changes are not processed until you press Analyze text.",
        )
    with right:
        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
        submitted = st.form_submit_button("Analyze text  →", type="primary", use_container_width=True)
        st.caption("Cached · private to this session")

if submitted:
    try:
        normalized = normalize_input(st.session_state.draft_text)
        started = time.perf_counter()
        _ = analyze(normalized)
        st.session_state.last_analysis_ms = int((time.perf_counter() - started) * 1000)
        st.session_state.analyzed_text = normalized
        st.toast("Analysis complete", icon="✅")
    except ValueError as exc:
        st.error(str(exc))
    except Exception as exc:
        st.error("The NLP pipeline could not process this input. Please simplify the text and try again.")
        st.caption(f"Technical detail: {type(exc).__name__}")

try:
    doc = analyze(st.session_state.analyzed_text)
except Exception:
    st.error("The NLP model could not initialize. Verify that the spaCy model from requirements.txt installed successfully.")
    st.stop()

relations = relationship_rows(doc)
summary = analysis_summary(doc, relations)

metric_cols = st.columns(6)
metric_values = [
    ("Words", summary.words, f"{summary.characters:,} characters"),
    ("Sentences", summary.sentences, "Detected boundaries"),
    ("Entities", summary.entities, "Named mentions"),
    ("Relations", summary.relationships, "SVO triples"),
    ("POS classes", summary.unique_pos, "Unique categories"),
    ("Pipeline", "Ready", f"{st.session_state.last_analysis_ms or 0} ms last submit" if st.session_state.last_analysis_ms is not None else "Cached sample"),
]
for col, (label, value, sub) in zip(metric_cols, metric_values):
    with col:
        metric_card(label, value, sub)

st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

tabs = st.tabs(
    [
        "Overview",
        "1 · Entity relations",
        "2 · POS tagging",
        "3 · POS distribution",
        "4 · Lemmatization",
        "5 · Stemming",
        "6 · Morphology",
        "7 · Dependencies",
    ]
)

# Precompute tables once per rerun. These operations are cheap after spaCy parsing.
entity_df = entity_rows(doc)
pos_df = token_rows(doc)
dist_df = pos_distribution(doc)
lemma_df = lemma_rows(doc)
stem_df = stem_rows(doc)
morph_df = morphology_rows(doc)
expanded_morph_df = expanded_morphology_rows(doc)
sent_df = sentence_rows(doc)

with tabs[0]:
    section_header("Workspace summary", "Analysis at a glance", "A compact overview of sentence structure, detected entities and downloadable analysis artifacts.")
    ov1, ov2 = st.columns([1.4, 1])
    with ov1:
        st.markdown("#### Sentence map")
        st.dataframe(sent_df, use_container_width=True, hide_index=True, height=min(330, 90 + len(sent_df) * 36))
    with ov2:
        st.markdown("#### Dominant POS classes")
        if not dist_df.empty:
            st.plotly_chart(pos_donut_chart(dist_df.head(8)), use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("No word tokens detected.")

    st.markdown("#### Extracted relationships")
    if relations.empty:
        st.info("No clear subject–predicate–object relationship was detected. Try a sentence such as “Microsoft acquired GitHub in 2018.”")
    else:
        relation_pills(relations)

    summary_dict = {
        "characters": summary.characters,
        "words": summary.words,
        "sentences": summary.sentences,
        "entities": summary.entities,
        "relationships": summary.relationships,
        "unique_pos": summary.unique_pos,
    }
    tables = {
        "entities": entity_df,
        "relationships": relations,
        "pos_tagging": pos_df,
        "pos_distribution": dist_df,
        "lemmatization": lemma_df,
        "stemming": stem_df,
        "morphology": morph_df,
        "sentences": sent_df,
    }
    st.download_button(
        "Download complete analysis (.zip)",
        export_bundle(st.session_state.analyzed_text, tables, summary_dict),
        file_name="lexiscope_analysis.zip",
        mime="application/zip",
        use_container_width=False,
    )

with tabs[1]:
    section_header("Named-entity relationship", "Entities connected by syntax", "See named entities in context, then inspect transparent dependency-derived subject–relation–object triples.")

    if doc.ents:
        st.markdown("#### Entity highlighting")
        ent_html = displacy.render(doc, style="ent", page=False)
        components.html(
            f"<div style='font-family:Inter,system-ui;padding:12px 8px;line-height:2.45;font-size:16px;color:#111827'>{ent_html}</div>",
            height=260,
            scrolling=True,
        )
        ec1, ec2 = st.columns([3, 1])
        with ec1:
            label_filter = st.multiselect(
                "Entity labels",
                options=sorted(entity_df["Label"].unique().tolist()),
                default=sorted(entity_df["Label"].unique().tolist()),
            )
            filtered_entities = entity_df[entity_df["Label"].isin(label_filter)] if label_filter else entity_df.iloc[0:0]
            st.dataframe(filtered_entities, use_container_width=True, hide_index=True)
        with ec2:
            counts = entity_df["Label"].value_counts()
            st.markdown("**Entity mix**")
            for label, count in counts.items():
                st.metric(label, int(count), help=str(entity_df.loc[entity_df["Label"] == label, "Meaning"].iloc[0]))
    else:
        st.info("No named entities were detected in this passage.")

    st.divider()
    st.markdown("#### Relationship explorer")
    if relations.empty:
        st.info("No clear relationship triples were extracted from this text.")
    else:
        graph_rows = relations.head(24)
        graph = relationship_graph(graph_rows)
        if graph is not None:
            st.plotly_chart(graph, use_container_width=True, config={"displaylogo": False, "scrollZoom": True})
        if len(relations) > len(graph_rows):
            st.caption(f"Graph shows the first {len(graph_rows)} relationships for readability; the table and export include all {len(relations)}.")
        relation_pills(relations)
        st.dataframe(relations, use_container_width=True, hide_index=True)
        st.download_button("Export relationships", csv_bytes(relations), "entity_relationships.csv", "text/csv")
        st.caption("Relationship extraction is an interpretable dependency heuristic, not a separately trained relation-classification model.")

with tabs[2]:
    section_header("Part-of-speech tagging", "Inspect every token", "Filter the token stream by grammatical class and inspect fine tags, lemmas, dependencies, entity labels and morphology.")
    pos_options = sorted(pos_df["POS"].dropna().unique().tolist())
    filter_col, search_col = st.columns([1, 1])
    selected_pos = filter_col.multiselect("POS filter", pos_options, default=pos_options)
    token_search = search_col.text_input("Find token", placeholder="e.g. Microsoft, analyzed, students")

    filtered = pos_df[pos_df["POS"].isin(selected_pos)] if selected_pos else pos_df.iloc[0:0]
    if token_search.strip():
        filtered = filtered[filtered["Token"].str.contains(token_search.strip(), case=False, regex=False)]
    st.dataframe(filtered, use_container_width=True, hide_index=True, height=410)

    if not pos_df.empty:
        inspector_token = st.selectbox("Token inspector", range(len(pos_df)), format_func=lambda i: f"{pos_df.iloc[i]['Token']} · {pos_df.iloc[i]['POS']}")
        row = pos_df.iloc[inspector_token]
        i1, i2, i3, i4 = st.columns(4)
        i1.metric("POS", row["POS"])
        i2.metric("Fine tag", row["Fine tag"])
        i3.metric("Dependency", row["Dependency"])
        i4.metric("Head", row["Head"])
        st.caption(f"Lemma: **{row['Lemma']}** · Entity: **{row['Entity']}** · Morphology: **{row['Morphology']}**")
    st.download_button("Export POS table", csv_bytes(pos_df), "pos_tagging.csv", "text/csv")

with tabs[3]:
    section_header("POS distribution", "Grammar as a distribution", "Compare frequency and proportional share of predicted part-of-speech categories.")
    if dist_df.empty:
        st.info("No word tokens were found.")
    else:
        chart_mode = st.radio("Visualization", ["Frequency", "Composition"], horizontal=True, label_visibility="collapsed")
        if chart_mode == "Frequency":
            st.plotly_chart(pos_bar_chart(dist_df), use_container_width=True, config={"displaylogo": False})
        else:
            st.plotly_chart(pos_donut_chart(dist_df), use_container_width=True, config={"displaylogo": False})
        st.dataframe(dist_df, use_container_width=True, hide_index=True)

with tabs[4]:
    section_header("Lemmatization", "Words reduced by linguistic context", "Compare each surface token with spaCy's context-sensitive dictionary/base form.")
    changed_lemmas = int((lemma_df["Changed"] == "Yes").sum()) if not lemma_df.empty else 0
    l1, l2, l3 = st.columns(3)
    l1.metric("Tokens evaluated", len(lemma_df))
    l2.metric("Changed forms", changed_lemmas)
    l3.metric("Unchanged", max(len(lemma_df) - changed_lemmas, 0))
    st.dataframe(lemma_df, use_container_width=True, hide_index=True, height=360)
    comp1, comp2 = st.columns(2)
    with comp1:
        st.markdown("**Original sequence**")
        st.info(" ".join(t.text for t in doc if not t.is_space))
    with comp2:
        st.markdown("**Lemmatized sequence**")
        st.success(" ".join(t.lemma_ for t in doc if not t.is_space))

with tabs[5]:
    section_header("Stemming", "Rule-based word reduction", "NLTK's PorterStemmer removes affixes mechanically, so stems may not be dictionary words.")
    changed_stems = int((stem_df["Changed"] == "Yes").sum()) if not stem_df.empty else 0
    s1, s2, s3 = st.columns(3)
    s1.metric("Tokens evaluated", len(stem_df))
    s2.metric("Changed forms", changed_stems)
    s3.metric("Algorithm", "Porter")
    st.dataframe(stem_df, use_container_width=True, hide_index=True, height=360)
    st.markdown("**Stemmed sequence**")
    st.code(" ".join(stem_df["Stem"].astype(str).tolist()), language=None, wrap_lines=True)

with tabs[6]:
    section_header("Morphological analysis", "Grammatical features at token level", "Inspect tense, number, person, degree, verb form, pronoun type and other available morphological features.")
    st.dataframe(morph_df, use_container_width=True, hide_index=True, height=330)
    if expanded_morph_df.empty:
        st.info("No explicit morphological features were predicted for these tokens.")
    else:
        available_features = sorted(expanded_morph_df["Feature"].unique().tolist())
        feature_filter = st.multiselect("Feature explorer", available_features, default=available_features[: min(5, len(available_features))])
        expanded_filtered = expanded_morph_df[expanded_morph_df["Feature"].isin(feature_filter)] if feature_filter else expanded_morph_df.iloc[0:0]
        st.dataframe(expanded_filtered, use_container_width=True, hide_index=True, height=300)

with tabs[7]:
    section_header("Dependency parsing", "Syntactic structure · style=dep", "Select a sentence to visualize head–dependent arcs, then inspect each dependency in a structured table.")
    sentences = list(doc.sents)
    if not sentences:
        st.info("No sentence boundary was detected.")
    else:
        sentence_idx = st.selectbox(
            "Sentence",
            range(len(sentences)),
            format_func=lambda i: f"{i + 1}. {sentences[i].text.strip()[:150]}{'…' if len(sentences[i].text.strip()) > 150 else ''}",
        )
        sentence = sentences[sentence_idx]
        dep_html = displacy.render(
            sentence,
            style="dep",
            page=False,
            options={"compact": False, "distance": 108, "add_lemma": True, "fine_grained": False},
        )
        components.html(
            f"<div style='overflow-x:auto;background:#fff;padding:18px 12px;border:1px solid #eaecf0;border-radius:16px'>{dep_html}</div>",
            height=485,
            scrolling=True,
        )
        dep_df = dependency_rows(sentence)
        st.dataframe(dep_df, use_container_width=True, hide_index=True)
        root_token = next((t for t in sentence if t.dep_ == "ROOT"), None)
        if root_token is not None:
            st.caption(f"Sentence root: **{root_token.text}** · lemma **{root_token.lemma_}** · POS **{root_token.pos_}**")
        st.download_button("Export dependency table", csv_bytes(dep_df), f"dependencies_sentence_{sentence_idx + 1}.csv", "text/csv")

st.markdown("---")
st.caption("LexiScope · Problem Statement 5 · spaCy + NLTK + Plotly + Streamlit · Educational NLP analysis workspace")
