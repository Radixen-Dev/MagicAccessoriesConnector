#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

REMOVE_BLUEUTIL=1
ASSUME_YES=0

confirm_step() {
  local prompt="$1"

  if [[ "$ASSUME_YES" -eq 1 ]]; then
    return 0
  fi

  printf "%s [y/N] " "$prompt"
  read -r answer
  case "$answer" in
    y|Y|yes|YES)
      return 0
      ;;
    *)
      return 1
      ;;
  esac
}

usage() {
  cat <<'EOF'
Usage: ./uninstall.sh [options]

Removes files created by install.sh and build.sh.

Options:
  --keep-blueutil   Do not uninstall Homebrew blueutil
  --yes             Do not prompt before any removal step
  --help            Show this help message
EOF
}

for arg in "$@"; do
  case "$arg" in
    --keep-blueutil)
      REMOVE_BLUEUTIL=0
      ;;
    --yes)
      ASSUME_YES=1
      ;;
    --help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $arg"
      usage
      exit 1
      ;;
  esac
done

echo "Uninstalling MagicAccessoriesConnector artifacts from: $ROOT_DIR"

# Remove project-local artifacts created by install/build scripts.
TARGETS=(
  ".venv"
  "build"
  "dist"
  "third_party"
)

for target in "${TARGETS[@]}"; do
  if [[ -e "$target" ]]; then
    if confirm_step "Remove $target?"; then
      rm -rf "$target"
      echo "Removed: $target"
    else
      echo "Skipped: $target"
    fi
  fi
done

# Remove Python bytecode caches created during app runs/builds.
if confirm_step "Remove Python cache files (__pycache__ and *.pyc)?"; then
  find "$ROOT_DIR" -type d -name "__pycache__" -prune -exec rm -rf {} + 2>/dev/null || true
  find "$ROOT_DIR" -type f -name "*.pyc" -delete 2>/dev/null || true
  echo "Removed: Python cache files"
else
  echo "Skipped: Python cache files"
fi

if [[ "$REMOVE_BLUEUTIL" -eq 1 ]]; then
  if command -v brew >/dev/null 2>&1; then
    if brew list --versions blueutil >/dev/null 2>&1; then
      if confirm_step "Homebrew blueutil is installed. Uninstall it?"; then
        brew uninstall blueutil
        echo "Removed: Homebrew formula blueutil"
      else
        echo "Kept: Homebrew formula blueutil"
      fi
    else
      echo "Homebrew is installed, but formula blueutil is not installed"
    fi
  else
    echo "Homebrew is not available in PATH; cannot check/uninstall formula blueutil"
  fi
else
  echo "Skipped Homebrew blueutil uninstall (--keep-blueutil)"
fi

echo "Done."
