#!/usr/bin/env bash
set -euo pipefail

if ! python3 -m venv /tmp/microscopyai-venv-check 2>/dev/null; then
  sudo apt-get update -qq
  sudo apt-get install -y -qq python3.12-venv
fi
rm -rf /tmp/microscopyai-venv-check

VENV_DIR="${HOME}/.venv/microscopyai"

if [[ ! -d "$VENV_DIR" ]]; then
  python3 -m venv "$VENV_DIR"
fi

# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"

python -m pip install --upgrade pip
pip install -r backend/requirements.txt

if [[ ! -f frontend/node_modules/.package-lock.json ]]; then
  cd frontend && npm install && cd ..
fi

if [[ ! -f frontend/public/demo/demo_result.json ]]; then
  PYTHONPATH="$(pwd)" python backend/scripts/generate_samples.py
fi
