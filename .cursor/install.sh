#!/usr/bin/env bash
set -euo pipefail

if ! python3 -m venv /tmp/aganitha-venv-check 2>/dev/null; then
  sudo apt-get update -qq
  sudo apt-get install -y -qq python3.12-venv
fi
rm -rf /tmp/aganitha-venv-check

VENV_DIR="${HOME}/.venv/aganitha"

if [[ ! -d "$VENV_DIR" ]]; then
  python3 -m venv "$VENV_DIR"
fi

# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"

python -m pip install --upgrade pip
pip install -e ".[dev]"
