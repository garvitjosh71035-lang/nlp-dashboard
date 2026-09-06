from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Iterable

import pandas as pd
import spacy
from nltk.stem import PorterStemmer
from spacy.tokens import Doc, Span, Token

MODEL_NAME = "en_core_web_sm"
MAX_TEXT_CHARS = 15_000

SUBJECT_DEPS = {"nsubj", "nsubjpass", "csubj", "csubjpass"}
OBJECT_DEPS = {"dobj", "obj", "attr", "oprd", "dative"}
PREP_OBJECT_DEPS = {"pobj", "obj"}


@dataclass(frozen=True)
class AnalysisSummary:
    characters: int
    words: int
    sentences: int
    entities: int
    unique_pos: int
    relationships: int


def load_model():
    """Load the English spaCy pipeline used by the dashboard."""
    return spacy.load(MODEL_NAME)


def normalize_input(text: str) -> str:
    """Normalize user input and enforce a predictable production bound."""
    normalized = " ".join(text.replace("\x00", " ").split())
    if not normalized:
        raise ValueError("Enter some English text to analyze.")
    if len(normalized) > MAX_TEXT_CHARS:
        raise ValueError(
            f"Text is too long ({len(normalized):,} characters). "
            f"Please keep the input below {MAX_TEXT_CHARS:,} characters."
        )
    return normalized


def serialize_doc(nlp, text: str) -> bytes:
    """Analyze text and serialize the Doc so results can be cached safely."""
    normalized = normalize_input(text)
    return nlp(normalized).to_bytes()


def restore_doc(nlp, payload: bytes) -> Doc:
    return Doc(nlp.vocab).from_bytes(payload)


def analysis_summary(doc: Doc, relationships: pd.DataFrame | None = None) -> AnalysisSummary:
    word_tokens = [t for t in doc if not t.is_space and not t.is_punct]
    rel_count = len(relationships) if relationships is not None else len(relationship_rows(doc))
    return AnalysisSummary(
        characters=len(doc.text),
        words=len(word_tokens),
        sentences=len(list(doc.sents)),
        entities=len(doc.ents),
        unique_pos=len({t.pos_ for t in word_tokens}),
        relationships=rel_count,
    )


def token_rows(doc: Doc) -> pd.DataFrame:
    rows = []
    for idx, token in enumerate(doc):
        if token.is_space:
            continue
        rows.append(
            {
                "#": idx + 1,
                "Token": token.text,
                "POS": token.pos_,
                "Fine tag": token.tag_,
                "Lemma": token.lemma_,
                "Dependency": token.dep_,
                "Head": token.head.text,
                "Entity": token.ent_type_ or "—",
                "Morphology": str(token.morph) or "—",
            }
        )
    return pd.DataFrame(rows)


def entity_rows(doc: Doc) -> pd.DataFrame:
    rows = [
        {
            "Entity": ent.text,
            "Label": ent.label_,
            "Meaning": spacy.explain(ent.label_) or "—",
            "Sentence": ent.sent.text.strip(),
            "Start": ent.start_char,
            "End": ent.end_char,
        }
        for ent in doc.ents
    ]
    return pd.DataFrame(rows)


def pos_distribution(doc: Doc) -> pd.DataFrame:
    counts = Counter(token.pos_ for token in doc if not token.is_space and not token.is_punct)
    total = sum(counts.values())
    rows = [
        {
            "POS": pos,
            "Count": count,
            "Share (%)": round((count / total) * 100, 2) if total else 0.0,
            "Meaning": spacy.explain(pos) or "—",
        }
        for pos, count in counts.most_common()
    ]
    return pd.DataFrame(rows)


def lemma_rows(doc: Doc) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "Token": token.text,
                "Lemma": token.lemma_,
                "Changed": "Yes" if token.text.lower() != token.lemma_.lower() else "No",
                "POS": token.pos_,
            }
            for token in doc
            if not token.is_space
        ]
    )


def stem_rows(doc: Doc) -> pd.DataFrame:
    stemmer = PorterStemmer()
    rows = []
    for token in doc:
        if token.is_space:
            continue
        stem = stemmer.stem(token.text) if token.is_alpha else token.text
        rows.append(
            {
                "Token": token.text,
                "Stem": stem,
                "Changed": "Yes" if token.text.lower() != stem.lower() else "No",
                "POS": token.pos_,
            }
        )
    return pd.DataFrame(rows)


def morphology_rows(doc: Doc) -> pd.DataFrame:
    rows = []
    for token in doc:
        if token.is_space:
            continue
        features = token.morph.to_dict()
        rows.append(
            {
                "Token": token.text,
                "POS": token.pos_,
                "Fine tag": token.tag_,
                "Morphology": str(token.morph) or "—",
                "Features": ", ".join(f"{k}={v}" for k, v in features.items()) or "—",
            }
        )
    return pd.DataFrame(rows)


def expanded_morphology_rows(doc: Doc) -> pd.DataFrame:
    rows = []
    for token in doc:
        if token.is_space:
            continue
        for feature, value in token.morph.to_dict().items():
            rows.append(
                {
                    "Token": token.text,
                    "POS": token.pos_,
                    "Feature": feature,
                    "Value": value,
                }
            )
    return pd.DataFrame(rows)


def dependency_rows(span: Span) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "Token": token.text,
                "Dependency": token.dep_,
                "Meaning": spacy.explain(token.dep_) or "—",
                "Head": token.head.text,
                "POS": token.pos_,
                "Lemma": token.lemma_,
                "Children": ", ".join(child.text for child in token.children) or "—",
            }
            for token in span
            if not token.is_space
        ]
    )


def _compact_phrase(token: Token) -> str:
    """Return a readable noun phrase while avoiding an entire long clause."""
    allowed_deps = {
        "det",
        "amod",
        "compound",
        "poss",
        "nummod",
        "quantmod",
        "case",
        "appos",
        "flat",
        "fixed",
        "name",
    }
    members = [token]
    for child in token.subtree:
        if child.i == token.i:
            continue
        if child.dep_ in allowed_deps and abs(child.i - token.i) <= 6:
            members.append(child)
    members = sorted(set(members), key=lambda t: t.i)
    return " ".join(t.text for t in members).strip()


def _best_entity_for_token(doc: Doc, token: Token) -> tuple[str, str]:
    for ent in doc.ents:
        if ent.start <= token.i < ent.end:
            return ent.text, ent.label_
    return _compact_phrase(token), "—"


def _subjects_for_verb(verb: Token) -> list[Token]:
    subjects = [child for child in verb.children if child.dep_ in SUBJECT_DEPS]
    if subjects:
        return subjects

    # Coordinated predicates often inherit the subject from their head verb.
    if verb.dep_ == "conj" and verb.head.pos_ in {"VERB", "AUX"}:
        subjects = [child for child in verb.head.children if child.dep_ in SUBJECT_DEPS]
    return subjects


def _object_candidates(verb: Token) -> list[tuple[str, Token]]:
    candidates: list[tuple[str, Token]] = []

    for child in verb.children:
        if child.dep_ in OBJECT_DEPS:
            candidates.append((verb.lemma_, child))

        if child.dep_ in {"prep", "agent"}:
            for pobj in child.children:
                if pobj.dep_ in PREP_OBJECT_DEPS:
                    candidates.append((f"{verb.lemma_} {child.text}", pobj))

    # Open clausal complements are useful for constructions such as
    # "Google plans to acquire X". Keep the relation human-readable.
    for child in verb.children:
        if child.dep_ in {"xcomp", "ccomp"} and child.pos_ in {"VERB", "AUX"}:
            for relation, obj in _object_candidates(child):
                candidates.append((f"{verb.lemma_} to {relation}", obj))

    return candidates


def relationship_rows(doc: Doc) -> pd.DataFrame:
    """Extract transparent dependency-based subject–relation–object triples.

    This is intentionally interpretable rather than pretending to be a trained
    relation-extraction model. It handles direct/prepositional objects,
    coordinated verbs, passive constructions, and entity labeling.
    """
    rows: list[dict] = []
    seen: set[tuple[str, str, str, str]] = set()

    for sent in doc.sents:
        for verb in sent:
            if verb.pos_ not in {"VERB", "AUX"}:
                continue

            subjects = _subjects_for_verb(verb)
            candidates = _object_candidates(verb)
            if not subjects or not candidates:
                continue

            passive = any(child.dep_ in {"nsubjpass", "auxpass"} for child in verb.children)

            for subject in subjects:
                subject_text, subject_type = _best_entity_for_token(doc, subject)
                for relation, obj in candidates:
                    object_text, object_type = _best_entity_for_token(doc, obj)

                    # For passive voice with an agent, present the semantic actor first
                    # when possible: "GitHub was acquired by Microsoft" -> Microsoft acquire GitHub.
                    relation_clean = relation.replace(" be ", " ").strip()
                    if passive and " by" in relation_clean:
                        display_subject, display_subject_type = object_text, object_type
                        display_object, display_object_type = subject_text, subject_type
                        relation_clean = relation_clean.replace(" by", "")
                    else:
                        display_subject, display_subject_type = subject_text, subject_type
                        display_object, display_object_type = object_text, object_type

                    key = (
                        display_subject.lower(),
                        relation_clean.lower(),
                        display_object.lower(),
                        sent.text.strip(),
                    )
                    if key in seen:
                        continue
                    seen.add(key)
                    rows.append(
                        {
                            "Subject": display_subject,
                            "Subject type": display_subject_type,
                            "Relation": relation_clean,
                            "Object": display_object,
                            "Object type": display_object_type,
                            "Sentence": sent.text.strip(),
                            "Confidence": "Rule-based",
                        }
                    )

    return pd.DataFrame(rows)


def sentence_rows(doc: Doc) -> pd.DataFrame:
    rows = []
    for i, sent in enumerate(doc.sents, start=1):
        tokens = [t for t in sent if not t.is_space and not t.is_punct]
        entities = [ent.text for ent in sent.ents]
        rows.append(
            {
                "Sentence": i,
                "Text": sent.text.strip(),
                "Words": len(tokens),
                "Entities": ", ".join(entities) or "—",
                "Root": next((t.text for t in sent if t.dep_ == "ROOT"), "—"),
            }
        )
    return pd.DataFrame(rows)


def csv_bytes(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8")
