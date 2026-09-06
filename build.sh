#!/usr/bin/env bash

set -euo pipefail

echo "Creating deployment virtual environment..."
rm -rf .venv
python3 -m venv .venv

echo "Installing Python dependencies..."
.venv/bin/python -m pip install --disable-pip-version-check -r requirements.txt

echo "Build completed successfully."