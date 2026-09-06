#!/usr/bin/env bash

set -euo pipefail

PORT_TO_USE="${PORT:-8501}"

exec .venv/bin/python -m streamlit run app.py \
  --server.address=0.0.0.0 \
  --server.port="${PORT_TO_USE}" \
  --server.headless=true \
  --server.runOnSave=false \
  --server.fileWatcherType=none