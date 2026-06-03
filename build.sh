#!/usr/bin/env bash
# build.sh — Builds the standalone MagicAccessoriesConnector.app and packages
# it as a zip for Homebrew Cask distribution.
#
# Output:
#   dist/MagicAccessoriesConnector.app
#   dist/MagicAccessoriesConnector-<VERSION>.zip
#
# After running this script:
#   1. Upload the zip to the GitHub release as a release asset.
#   2. Copy the printed SHA256 into the Cask file.
set -euo pipefail

VERSION="1.2.1"
ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

# ── Python virtualenv ─────────────────────────────────────────────────────────
if [[ ! -d .venv ]]; then
  python3 -m venv .venv
fi

source .venv/bin/activate
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt pyinstaller

# ── PyInstaller build ─────────────────────────────────────────────────────────
pyinstaller --noconfirm MagicAccessoriesConnector.spec

# ── Package as zip for Cask ───────────────────────────────────────────────────
ZIP_NAME="MagicAccessoriesConnector-${VERSION}.zip"
cd dist
# Remove any previous zip to get a stable SHA256.
rm -f "$ZIP_NAME"
zip -r --symlinks "$ZIP_NAME" MagicAccessoriesConnector.app
cd "$ROOT_DIR"

SHA256=$(shasum -a 256 "dist/$ZIP_NAME" | awk '{print $1}')

echo ""
echo "Build complete."
echo "  App:  dist/MagicAccessoriesConnector.app"
echo "  Zip:  dist/$ZIP_NAME"
echo "  SHA256: $SHA256"
echo ""
echo "Next steps:"
echo "  1. Upload dist/$ZIP_NAME to the v${VERSION} GitHub release."
echo "  2. Set sha256 \"$SHA256\" in Casks/magic-accessories-connector.rb."
