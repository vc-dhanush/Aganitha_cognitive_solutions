#!/usr/bin/env bash
set -euo pipefail

VENV_DIR="${HOME}/.venv/aganitha"

if [[ ! -d "$VENV_DIR" ]]; then
  python3 -m venv "$VENV_DIR"
fi

# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"

python -m pip install --upgrade pip
pip install -e ".[dev]"
