#!/usr/bin/env bash

set -euo pipefail

echo "Creating deployment virtual environment..."

rm -rf .venv
python3 -m venv .venv

echo "Preparing isolated pip environment..."

.venv/bin/python -m ensurepip --upgrade

echo "Installing Python dependencies..."

env \
  -u PIP_USER \
  -u PYTHONUSERBASE \
  PIP_CONFIG_FILE=/dev/null \
  .venv/bin/python -m pip --isolated install \
  --disable-pip-version-check \
  -r requirements.txt

echo "Build completed successfully."