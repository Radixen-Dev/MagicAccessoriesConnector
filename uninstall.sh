#!/usr/bin/env bash
# uninstall.sh — Removes all traces of MagicAccessoriesConnector from this machine.
#
# Handles both cases:
#   1. Installed via Homebrew (brew install magic-accessories-connector)
#   2. Run from source (./install.sh)
#
# Homebrew manages its own Cellar cleanup; this script additionally removes:
#   - The brew service (LaunchAgent)
#   - The Homebrew service log (brew uninstall does not remove this)
#   - User app data: ~/Library/Application Support/MagicAccessoriesConnector
#   - Dev artifacts: .venv, build, dist, third_party, Python caches
#   - Optionally: the Homebrew blueutil formula
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

Removes all traces of MagicAccessoriesConnector from this machine.
Handles both Homebrew-installed and run-from-source setups.

Options:
  --keep-blueutil   Do not uninstall Homebrew blueutil
  --yes             Skip all confirmation prompts
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

echo "Uninstalling MagicAccessoriesConnector..."
echo ""

# ── Step 1: Homebrew service ──────────────────────────────────────────────────
if command -v brew >/dev/null 2>&1; then
  if brew list --versions magic-accessories-connector >/dev/null 2>&1; then
    # Stop the service / LaunchAgent first.
    if brew services list | grep -q "^magic-accessories-connector.*started"; then
      if confirm_step "Stop brew service magic-accessories-connector?"; then
        brew services stop magic-accessories-connector
        echo "Stopped: brew service magic-accessories-connector"
      else
        echo "Warning: service still running; it may restart after uninstall."
      fi
    fi

    if confirm_step "Uninstall Homebrew formula magic-accessories-connector?"; then
      brew uninstall magic-accessories-connector
      echo "Removed: Homebrew formula magic-accessories-connector"
    else
      echo "Skipped: Homebrew formula uninstall"
    fi

    # Remove the Homebrew service log — brew uninstall does NOT remove it.
    BREW_LOG="$(brew --prefix)/var/log/magic-accessories-connector.log"
    if [[ -f "$BREW_LOG" ]]; then
      if confirm_step "Remove Homebrew service log at $BREW_LOG?"; then
        rm -f "$BREW_LOG"
        echo "Removed: $BREW_LOG"
      else
        echo "Kept: $BREW_LOG"
      fi
    fi
  else
    echo "Info: magic-accessories-connector is not installed via Homebrew; skipping formula removal."
  fi
else
  echo "Info: Homebrew not found; skipping formula removal."
fi

# ── Step 2: User app data ─────────────────────────────────────────────────────
APP_SUPPORT_DIR="$HOME/Library/Application Support/MagicAccessoriesConnector"
if [[ -d "$APP_SUPPORT_DIR" ]]; then
  if confirm_step "Remove saved app data at ~/Library/Application Support/MagicAccessoriesConnector?"; then
    rm -rf "$APP_SUPPORT_DIR"
    echo "Removed: ~/Library/Application Support/MagicAccessoriesConnector"
  else
    echo "Kept: ~/Library/Application Support/MagicAccessoriesConnector"
  fi
else
  echo "Info: No saved app data found at ~/Library/Application Support/MagicAccessoriesConnector"
fi

# ── Step 3: Dev-mode artifacts (only present if run via ./install.sh) ─────────
DEV_TARGETS=(".venv" "build" "dist" "third_party")
for target in "${DEV_TARGETS[@]}"; do
  if [[ -e "$ROOT_DIR/$target" ]]; then
    if confirm_step "Remove dev artifact: $target?"; then
      rm -rf "${ROOT_DIR:?}/$target"
      echo "Removed: $target"
    else
      echo "Skipped: $target"
    fi
  fi
done

# ── Step 4: Python bytecode caches ───────────────────────────────────────────
PYCACHE_FOUND=0
if find "$ROOT_DIR" -type d -name "__pycache__" 2>/dev/null | grep -q .; then
  PYCACHE_FOUND=1
fi
if find "$ROOT_DIR" -type f -name "*.pyc" 2>/dev/null | grep -q .; then
  PYCACHE_FOUND=1
fi

if [[ "$PYCACHE_FOUND" -eq 1 ]]; then
  if confirm_step "Remove Python cache files (__pycache__ and *.pyc)?"; then
    find "$ROOT_DIR" -type d -name "__pycache__" -prune -exec rm -rf {} + 2>/dev/null || true
    find "$ROOT_DIR" -type f -name "*.pyc" -delete 2>/dev/null || true
    echo "Removed: Python cache files"
  else
    echo "Skipped: Python cache files"
  fi
fi

# ── Step 5: Homebrew blueutil (optional) ─────────────────────────────────────
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
      echo "Info: Homebrew is present but blueutil is not installed via it."
    fi
  else
    echo "Info: Homebrew not found; skipping blueutil removal."
  fi
else
  echo "Skipped: blueutil removal (--keep-blueutil)"
fi

echo ""
echo "Done."
