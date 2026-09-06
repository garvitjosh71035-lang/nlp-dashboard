# LexiScope — Production-Style Interactive NLP Dashboard

**Problem Statement 5:** Build a dashboard that lets a user perform:

1. Named-Entity Relationship
2. POS Tagging
3. POS Distribution
4. Lemmatization
5. Stemming
6. Morphology
7. Dependencies (`style="dep"`)

LexiScope is a GitHub/Replit-ready Streamlit application built around **spaCy**, **NLTK**, **Plotly**, and **pandas**. The UI is structured as a modern analysis workspace rather than a collection of disconnected classroom widgets.

## Product experience

- Modern responsive landing/workspace layout
- Explicit **Analyze text** workflow instead of processing every keystroke
- Cached serialized spaCy results to reduce repeated compute
- Built-in sample texts and `.txt` import
- Six top-level analysis metrics
- Overview workspace with sentence map and downloadable analysis bundle
- Entity highlighting and label filters
- Interactive directional relationship graph
- Filterable POS table and per-token inspector
- Frequency/composition POS visualizations
- Lemmatization and stemming change statistics
- Morphology feature explorer
- Sentence-selectable displaCy dependency visualization
- CSV exports for individual analyses
- One-click ZIP containing the complete analysis
- Input length validation and user-facing failure states

## NLP/backend behavior

### Named-Entity Relationship

The dashboard performs two related operations:

- **Named Entity Recognition (NER)** using spaCy's NER component.
- **Relationship extraction** using an interpretable dependency heuristic that derives subject–predicate–object triples.

The relationship extractor handles direct objects, prepositional objects, coordinated predicates, basic passive constructions, and named-entity labels. It is intentionally presented as rule/dependency-based extraction rather than falsely claiming to be a separately trained relation classifier.

### POS + morphology

For each token the dashboard exposes:

- coarse POS
- fine-grained tag
- lemma
- dependency label
- syntactic head
- entity label
- morphology

### Lemmatization vs stemming

- Lemmatization uses spaCy's context-sensitive linguistic pipeline.
- Stemming uses NLTK's `PorterStemmer` and is clearly separated from lemmatization because a stem does not have to be a dictionary word.

### Dependencies

Each sentence can be selected independently and rendered with:

```python
displacy.render(sentence, style="dep", ...)
```

The dashboard also provides a structured dependency table for the selected sentence.

## Project structure

```text
nlp-dashboard/
├── app.py                         # Streamlit application/controller
├── nlp_utils.py                   # NLP processing + relation extraction
├── visualizations.py              # Plotly chart/graph builders
├── ui.py                          # App visual system + reusable UI fragments
├── requirements.txt               # Runtime dependencies
├── requirements-dev.txt           # Test dependencies
├── run.sh                         # Replit/local production launcher
├── .replit
├── .streamlit/
│   └── config.toml
├── scripts/
│   └── health_monitor.py          # Streamlit health endpoint probe
├── tests/
│   └── test_nlp_utils.py          # Core NLP tests
└── .github/workflows/
    ├── health-check.yml            # 30-minute production health monitoring
    └── tests.yml                   # CI on push / pull request
```

## Run locally

Python 3.11 is recommended.

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

macOS/Linux:

```bash
source .venv/bin/activate
pip install -r requirements.txt
bash run.sh
```

## Run tests

```bash
pip install -r requirements-dev.txt
pytest -q
```

GitHub Actions runs the same backend tests on every push and pull request to `main`.

## GitHub → Replit

Push the extracted project to GitHub:

```bash
git init
git add .
git commit -m "Build LexiScope NLP dashboard"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
git push -u origin main
```

Then import that repository into Replit. The included launcher runs:

```bash
streamlit run app.py --server.address=0.0.0.0 --server.port=$PORT
```

The `.streamlit/config.toml` also enables headless operation, XSRF protection, CORS and a small upload limit suitable for this text-analysis application.

## 30-minute health monitor

The existing monitor remains deliberately set to **twice per hour**, at minutes **17 and 47**:

```yaml
schedule:
  - cron: "17,47 * * * *"
```

It calls Streamlit's health endpoint:

```text
https://YOUR-DEPLOYMENT/_stcore/health
```

and retries transient failures before marking the GitHub Actions run unhealthy.

### Configure health monitoring

In the GitHub repository:

1. Open **Settings → Secrets and variables → Actions**.
2. Add a repository secret named `APP_URL`.
3. Set it to your published Replit URL, e.g. `https://your-app.replit.app`.
4. Open **Actions → Continuous dashboard health monitor**.
5. Run it manually once to verify the URL.

For genuine continuous compute, deploy on a Replit option intended to remain running continuously; use the GitHub workflow as an independent health signal rather than treating cron traffic as the hosting layer.

## Suggested demonstration inputs

### Relationships

```text
Microsoft acquired GitHub in 2018. Satya Nadella leads Microsoft and the company partners with OpenAI.
```

### General NLP

```text
The curious students carefully analyzed several difficult sentences and presented their findings to the professor.
```

### Named entities

```text
Alice travelled from Delhi to Budapest on Monday and met researchers from Eötvös Loránd University.
```

## Design choices for grading/viva

- **NER** identifies spans such as people, organizations, places and dates.
- **Relation extraction** links syntactic subjects, predicates and objects using dependencies.
- **POS tagging** assigns grammatical categories to tokens.
- **POS distribution** summarizes how often those categories appear.
- **Lemmatization** maps a token to a contextual dictionary/base form.
- **Stemming** reduces words mechanically and may produce non-dictionary forms.
- **Morphology** exposes grammatical features such as tense, number, person, degree and verb form.
- **Dependency parsing** predicts head–dependent syntactic relationships between tokens.

The application intentionally keeps the backend logic explainable, which makes it suitable for both demonstration and viva questions.
