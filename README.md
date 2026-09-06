# Mobile-friendly NLP Dashboard

A simple, production-oriented Streamlit interface for seven NLP operations:

1. Named-Entity Relationship
2. POS Tagging
3. POS Distribution
4. Lemmatization
5. Stemming
6. Morphology
7. Dependencies (`style="dep"`)

## UX model

The interface intentionally avoids complex tabs and sidebars:

1. Paste text.
2. Press **Analyze text** once.
3. Select one of seven large operation buttons.
4. View only the selected result.

On screens below 700px the action buttons, metrics, and control rows stack into a single column. Dependency diagrams are horizontally swipeable so wide syntax trees do not break mobile layout.

## Local run

```bash
python -m pip install -r requirements.txt
bash run.sh
```

On Windows PowerShell you can instead run:

```powershell
python -m pip install -r requirements.txt
streamlit run app.py
```

## Replit

The repository includes `.replit` and `run.sh`. Import the GitHub repository into Replit and run it. The deployment command listens on `0.0.0.0` and uses Replit's `$PORT`.

## Health monitor

`.github/workflows/health-check.yml` runs at:

```text
17 and 47 minutes past every hour
```

That is a 30-minute cadence:

```yaml
cron: "17,47 * * * *"
```

Add a GitHub Actions repository secret named `APP_URL` with the deployed Replit URL, for example:

```text
https://your-dashboard.replit.app
```

Do not append `/_stcore/health`; the monitor does that automatically.

Each run checks both:

- `/_stcore/health`
- the public root page

and retries up to five times before failing the workflow.
