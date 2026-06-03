#!/usr/bin/env bash
# install.sh — Developer run-from-source script.
#
# End-user installation (recommended):
#   brew tap Radixen-Dev/tap
#   brew install --cask magic-accessories-connector
#   Then launch from /Applications or click “Start at Login” in the menu.
#
# This script is for contributors running the app directly from source.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

if ! command -v brew >/dev/null 2>&1; then
  echo "Homebrew is required. Install it first: https://brew.sh"
  exit 1
fi

if ! command -v blueutil >/dev/null 2>&1; then
  brew install blueutil
fi

if [[ ! -d .venv ]]; then
  python3 -m venv .venv
fi

source .venv/bin/activate
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt

echo "Starting MagicAccessoriesConnector (dev mode)..."
OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES .venv/bin/python app.py
