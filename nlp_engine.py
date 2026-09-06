from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Any

import pandas as pd
import spacy
from nltk.stem import PorterStemmer
from spacy import displacy


_STEMMER = PorterStemmer()


POS_DESCRIPTIONS = {
    "ADJ": "Adjective",
    "ADP": "Adposition",
    "ADV": "Adverb",
    "AUX": "Auxiliary",
    "CCONJ": "Coordinating conjunction",
    "DET": "Determiner",
    "INTJ": "Interjection",
    "NOUN": "Noun",
    "NUM": "Numeral",
    "PART": "Particle",
    "PRON": "Pronoun",
    "PROPN": "Proper noun",
    "PUNCT": "Punctuation",
    "SCONJ": "Subordinating conjunction",
    "SYM": "Symbol",
    "VERB": "Verb",
    "X": "Other",
}


@dataclass(frozen=True)
class AnalysisResult:
    text: str
    summary: dict[str, int]
    entities: list[dict[str, Any]]
    relationships: list[dict[str, Any]]
    pos: list[dict[str, Any]]
    pos_distribution: list[dict[str, Any]]
    lemmas: list[dict[str, Any]]
    stems: list[dict[str, Any]]
    morphology: list[dict[str, Any]]
    dependency_sentences: list[dict[str, Any]]
    entity_html: str


def load_model():
    """Load the English spaCy pipeline.

    The model is installed through requirements.txt so deployment does not need
    a runtime model download.
    """
    return spacy.load("en_core_web_sm")


def _span_text(token) -> str:
    if token.ent_type_:
        return token.ent_iob_ and token.text or token.text
    return token.text


def _nearest_entity_for_token(token, doc):
    for ent in doc.ents:
        if ent.start <= token.i < ent.end:
            return ent
    return None


def _entity_or_phrase(token, doc):
    ent = _nearest_entity_for_token(token, doc)
    if ent is not None:
        return ent.text, ent.label_

    subtree = [t for t in token.subtree if not t.is_punct]
    if subtree:
        text = doc[subtree[0].i : subtree[-1].i + 1].text.strip()
    else:
        text = token.text
    return text, token.pos_


def _subject_candidates(verb):
    subjects = [
        child
        for child in verb.children
        if child.dep_ in {"nsubj", "nsubjpass", "csubj", "csubjpass", "expl"}
    ]
    if subjects:
        return subjects

    # Coordinated verb often inherits the subject from its head verb.
    if verb.dep_ == "conj" and verb.head.pos_ in {"VERB", "AUX"}:
        return _subject_candidates(verb.head)
    return []


def _object_candidates(verb):
    objects = [
        child
        for child in verb.children
        if child.dep_ in {"dobj", "obj", "attr", "oprd", "dative"}
    ]

    # Capture prepositional objects: works for / invested in / partnered with.
    for prep in [c for c in verb.children if c.dep_ == "prep"]:
        objects.extend([c for c in prep.children if c.dep_ == "pobj"])

    # Passive agent: "GitHub was acquired by Microsoft".
    for agent in [c for c in verb.children if c.dep_ == "agent"]:
        objects.extend([c for c in agent.children if c.dep_ == "pobj"])

    return objects


def _relation_label(verb, obj) -> str:
    label = verb.lemma_.lower() or verb.text.lower()
    if obj.head.dep_ == "prep" and obj.head.head == verb:
        label = f"{label} {obj.head.text.lower()}"
    return label


def extract_relationships(doc) -> list[dict[str, Any]]:
    """Extract readable subject-relation-object triples.

    This is intentionally a deterministic syntactic relation extractor rather
    than an ML relation classifier. It works well for classroom/demo sentences
    and avoids pretending that arbitrary relations are semantically verified.
    """
    rows: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str]] = set()

    for verb in [t for t in doc if t.pos_ in {"VERB", "AUX"}]:
        subjects = _subject_candidates(verb)
        objects = _object_candidates(verb)

        passive_subjects = [s for s in subjects if s.dep_ in {"nsubjpass", "csubjpass"}]
        agents = []
        for agent in [c for c in verb.children if c.dep_ == "agent"]:
            agents.extend([c for c in agent.children if c.dep_ == "pobj"])

        # Normalize passive voice when an explicit by-agent is available.
        if passive_subjects and agents:
            for agent in agents:
                for patient in passive_subjects:
                    subject_text, subject_type = _entity_or_phrase(agent, doc)
                    object_text, object_type = _entity_or_phrase(patient, doc)
                    key = (subject_text.lower(), verb.lemma_.lower(), object_text.lower())
                    if key not in seen:
                        seen.add(key)
                        rows.append(
                            {
                                "Subject": subject_text,
                                "Subject type": subject_type,
                                "Relation": verb.lemma_.lower(),
                                "Object": object_text,
                                "Object type": object_type,
                                "Sentence": verb.sent.text.strip(),
                            }
                        )
            continue

        for subject in subjects:
            for obj in objects:
                # Avoid treating an explicit passive agent as an ordinary object.
                if obj in agents:
                    continue
                subject_text, subject_type = _entity_or_phrase(subject, doc)
                object_text, object_type = _entity_or_phrase(obj, doc)
                relation = _relation_label(verb, obj)
                key = (subject_text.lower(), relation, object_text.lower())
                if key in seen:
                    continue
                seen.add(key)
                rows.append(
                    {
                        "Subject": subject_text,
                        "Subject type": subject_type,
                        "Relation": relation,
                        "Object": object_text,
                        "Object type": object_type,
                        "Sentence": verb.sent.text.strip(),
                    }
                )

    return rows


def analyze_text(text: str, nlp=None) -> AnalysisResult:
    cleaned = " ".join(text.split())
    if not cleaned:
        raise ValueError("Please enter some English text before analyzing.")

    if nlp is None:
        nlp = load_model()

    doc = nlp(cleaned)
    words = [t for t in doc if not t.is_space and not t.is_punct]

    entities = [
        {
            "Text": ent.text,
            "Label": ent.label_,
            "Meaning": spacy.explain(ent.label_) or ent.label_,
            "Start": ent.start_char,
            "End": ent.end_char,
        }
        for ent in doc.ents
    ]

    relationships = extract_relationships(doc)

    pos_rows = [
        {
            "Token": token.text,
            "POS": token.pos_,
            "POS meaning": POS_DESCRIPTIONS.get(token.pos_, token.pos_),
            "Fine tag": token.tag_,
            "Tag meaning": spacy.explain(token.tag_) or "—",
            "Lemma": token.lemma_,
            "Dependency": token.dep_,
            "Head": token.head.text,
            "Entity": token.ent_type_ or "—",
        }
        for token in doc
        if not token.is_space
    ]

    counts = Counter(token.pos_ for token in words)
    total_pos = sum(counts.values()) or 1
    pos_distribution = [
        {
            "POS": pos,
            "Meaning": POS_DESCRIPTIONS.get(pos, pos),
            "Count": count,
            "Percent": round((count / total_pos) * 100, 2),
        }
        for pos, count in counts.most_common()
    ]

    lemmas = [
        {
            "Token": token.text,
            "Lemma": token.lemma_,
            "Changed": token.text.lower() != token.lemma_.lower(),
        }
        for token in words
    ]

    stems = [
        {
            "Token": token.text,
            "Stem": _STEMMER.stem(token.text),
            "Changed": token.text.lower() != _STEMMER.stem(token.text).lower(),
        }
        for token in words
    ]

    morphology = []
    for token in words:
        features = token.morph.to_dict()
        morphology.append(
            {
                "Token": token.text,
                "POS": token.pos_,
                "Morphology": str(token.morph) if str(token.morph) else "—",
                "Features": features,
            }
        )

    dep_sentences = []
    for index, sent in enumerate(doc.sents, start=1):
        dep_sentences.append(
            {
                "index": index,
                "text": sent.text.strip(),
                "html": displacy.render(sent.as_doc(), style="dep", page=False, options={"compact": True}),
                "tokens": [
                    {
                        "Token": token.text,
                        "POS": token.pos_,
                        "Dependency": token.dep_,
                        "Dependency meaning": spacy.explain(token.dep_) or "—",
                        "Head": token.head.text,
                        "Lemma": token.lemma_,
                    }
                    for token in sent
                    if not token.is_space
                ],
            }
        )

    entity_html = displacy.render(doc, style="ent", page=False)

    summary = {
        "words": len(words),
        "sentences": len(list(doc.sents)),
        "entities": len(entities),
        "relationships": len(relationships),
        "pos_types": len(counts),
    }

    return AnalysisResult(
        text=cleaned,
        summary=summary,
        entities=entities,
        relationships=relationships,
        pos=pos_rows,
        pos_distribution=pos_distribution,
        lemmas=lemmas,
        stems=stems,
        morphology=morphology,
        dependency_sentences=dep_sentences,
        entity_html=entity_html,
    )


def to_dataframe(rows: list[dict[str, Any]]) -> pd.DataFrame:
    return pd.DataFrame(rows)
