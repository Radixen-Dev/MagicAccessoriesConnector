#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

if [[ ! -d .venv ]]; then
  python3 -m venv .venv
fi

source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt pyinstaller

mkdir -p third_party
if command -v blueutil >/dev/null 2>&1; then
  cp "$(command -v blueutil)" third_party/blueutil
  chmod +x third_party/blueutil
else
  echo "Warning: blueutil not found on PATH. The built app will require blueutil installed on the target machine."
fi

pyinstaller --noconfirm MagicAccessoriesConnector.spec

echo "Build complete: dist/MagicAccessoriesConnector.app"
