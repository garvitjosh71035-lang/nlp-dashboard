import pytest

from nlp_utils import (
    analysis_summary,
    entity_rows,
    load_model,
    normalize_input,
    pos_distribution,
    relationship_rows,
)


@pytest.fixture(scope="module")
def nlp():
    return load_model()


def test_normalize_input_rejects_empty():
    with pytest.raises(ValueError):
        normalize_input("   \n\t")


def test_core_tables(nlp):
    doc = nlp("Microsoft acquired GitHub in 2018.")
    assert not entity_rows(doc).empty
    assert not pos_distribution(doc).empty
    summary = analysis_summary(doc)
    assert summary.words >= 4
    assert summary.sentences == 1


def test_relationship_extraction(nlp):
    doc = nlp("Microsoft acquired GitHub in 2018.")
    rows = relationship_rows(doc)
    assert not rows.empty
    text = " ".join(rows.astype(str).values.flatten()).lower()
    assert "microsoft" in text
    assert "github" in text
