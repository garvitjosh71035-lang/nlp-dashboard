import spacy

from nlp_engine import analyze_text, extract_relationships


def test_blank_text_rejected():
    nlp = spacy.blank("en")
    try:
        analyze_text("   ", nlp)
    except ValueError:
        return
    raise AssertionError("blank text should raise ValueError")


def test_full_pipeline_with_installed_model():
    nlp = spacy.load("en_core_web_sm")
    result = analyze_text("Microsoft acquired GitHub in 2018.", nlp)
    assert result.summary["words"] >= 4
    assert any(row["Text"] == "Microsoft" for row in result.entities)
    assert any(row["Text"] == "GitHub" for row in result.entities)
    assert any(
        "Microsoft" in row["Subject"] and "GitHub" in row["Object"]
        for row in result.relationships
    )
    assert result.dependency_sentences


def test_passive_relationship_normalization():
    nlp = spacy.load("en_core_web_sm")
    doc = nlp("GitHub was acquired by Microsoft.")
    rows = extract_relationships(doc)
    assert any(
        "Microsoft" in row["Subject"] and "GitHub" in row["Object"]
        for row in rows
    )
