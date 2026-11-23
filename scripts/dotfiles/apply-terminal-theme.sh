#!/usr/bin/env bash
# Apply Gruvbox Dark terminal theme + Claude Code ANSI settings
# Idempotent — safe to re-run on any Linux machine
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=== Terminal & Claude Code Theme Sync ==="

# 1. Apply GNOME Terminal profile
if command -v dconf &>/dev/null; then
    echo "[1/3] Applying GNOME Terminal Gruvbox Dark profile..."
    dconf load /org/gnome/terminal/legacy/profiles:/ < "${SCRIPT_DIR}/gnome-terminal-profile.dconf"
    echo "  ✓ GNOME Terminal colors set (bg:#282828, fg:#ebdbb2)"
else
    echo "[1/3] SKIP: dconf not found (not GNOME Terminal?)"
    echo "  Manual: set background=#282828, foreground=#ebdbb2 in your terminal"
fi

# 2. Apply Claude Code theme
echo "[2/3] Setting Claude Code theme to dark-ansi..."
CLAUDE_SETTINGS="${HOME}/.claude/settings.json"
mkdir -p "${HOME}/.claude"
if [ -f "${CLAUDE_SETTINGS}" ]; then
    # Update existing settings — preserve other keys
    if command -v python3 &>/dev/null; then
        uv run --no-project python - "${CLAUDE_SETTINGS}" <<'PY'
import json, sys
settings_path = sys.argv[1]
with open(settings_path) as f:
    s = json.load(f)
s['theme'] = 'dark-ansi'
with open(settings_path, 'w') as f:
    json.dump(s, f, indent=2)
PY
    else
        echo '{"theme": "dark-ansi"}' > "${CLAUDE_SETTINGS}"
    fi
else
    echo '{"theme": "dark-ansi"}' > "${CLAUDE_SETTINGS}"
fi
echo "  ✓ Claude Code theme set to dark-ansi"

# 3. Verify
echo "[3/3] Verification..."
if command -v dconf &>/dev/null; then
    BG=$(dconf read /org/gnome/terminal/legacy/profiles:/:b1dcc9dd-5262-4d8d-a863-c897e6d979b9/background-color 2>/dev/null || echo "unknown")
    echo "  Terminal BG: ${BG}"
fi
echo "  Claude theme: $(uv run --no-project python - "${CLAUDE_SETTINGS}" <<'PY' 2>/dev/null || echo 'check manually'
import json, sys
print(json.load(open(sys.argv[1]))['theme'])
PY
)"

echo ""
echo "Done. Restart terminal to see changes."
