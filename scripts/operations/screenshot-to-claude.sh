#!/usr/bin/env bash
# screenshot-to-claude.sh — Copy "@<latest-screenshot-path>" to clipboard.
#
# Usage:
#   bash scripts/operations/screenshot-to-claude.sh
#   # Then Ctrl+Shift+V into Claude Code chat to paste the @-reference.
#
# Bind to a GNOME custom keyboard shortcut for one-key workflow:
#   Settings → Keyboard → Custom Shortcuts → Add:
#     Name: Screenshot to Claude
#     Command: /mnt/local-analysis/workspace-hub/scripts/operations/screenshot-to-claude.sh
#     Shortcut: (your choice, e.g. Super+S)
#
# Requires: xclip (sudo apt install xclip)

set -euo pipefail

SCREENSHOT_DIR="${CLAUDE_SCREENSHOT_DIR:-${HOME}/Pictures/Screenshots}"

if [[ ! -d "$SCREENSHOT_DIR" ]]; then
  echo "ERROR: Screenshot directory not found: $SCREENSHOT_DIR" >&2
  exit 1
fi

latest="$(ls -t "$SCREENSHOT_DIR"/*.png 2>/dev/null | head -1)"

if [[ -z "$latest" ]]; then
  echo "ERROR: No .png files found in $SCREENSHOT_DIR" >&2
  exit 1
fi

ref="@${latest}"
echo -n "$ref" | xclip -selection clipboard
echo "Copied to clipboard: $ref"
