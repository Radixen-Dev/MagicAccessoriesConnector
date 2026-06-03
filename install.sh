#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

if ! command -v brew >/dev/null 2>&1; then
  echo "Homebrew is required for one-command setup. Install Homebrew first: https://brew.sh"
  exit 1
fi

if ! command -v blueutil >/dev/null 2>&1; then
  brew install blueutil
fi

if [[ ! -d .venv ]]; then
  python3 -m venv .venv
fi

source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "Starting MagicAccessoriesConnector..."
.venv/bin/python app.py
