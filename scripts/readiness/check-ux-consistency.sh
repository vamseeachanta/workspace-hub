#!/usr/bin/env bash
# check-ux-consistency.sh — Cross-machine terminal UX consistency check (WRK-228).
# Validates: keybindings.json, CLAUDE_SCREENSHOT_DIR, Chrome Claude extension.
# Called standalone (wh-ux alias) or by nightly-readiness.sh (R-UX check).
# Returns 0 always — results are printed; use --strict to return 1 on any FAIL.
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_HUB="${WORKSPACE_HUB:-$(cd "${SCRIPT_DIR}/../.." && pwd)}"

STRICT=false
[[ "${1:-}" == "--strict" ]] && STRICT=true

PASS=0; WARN=0; FAIL=0

_pass() { echo "  PASS  $1"; PASS=$((PASS + 1)); }
_warn() { echo "  WARN  $1"; WARN=$((WARN + 1)); }
_fail() { echo "  FAIL  $1"; FAIL=$((FAIL + 1)); }

# ── Detect platform ───────────────────────────────────────────────────────────
WH_OS="linux"
case "$(uname -s 2>/dev/null)" in
  MINGW*|CYGWIN*|MSYS*) WH_OS="windows" ;;
esac
HOSTNAME_SHORT=$(hostname -s 2>/dev/null || hostname | cut -d. -f1 | tr '[:upper:]' '[:lower:]')

echo "=== UX consistency check (WRK-228) ==="
echo "    Host: ${HOSTNAME_SHORT}  OS: ${WH_OS}  Date: $(date +%Y-%m-%d)"
echo ""

# ─────────────────────────────────────────────────────────────────────────────
# UX-1: Keybindings file present and submitPrompt = ctrl+enter
# ─────────────────────────────────────────────────────────────────────────────
echo "--- Keybindings"
KEYBINDINGS_FILE="${HOME}/.claude/keybindings.json"
KEYBINDINGS_SRC="${WORKSPACE_HUB}/config/claude/keybindings.json"

if [[ ! -f "$KEYBINDINGS_FILE" ]]; then
  _fail "~/.claude/keybindings.json absent — submit key inconsistent across machines"
  echo "       Fix: cp '${KEYBINDINGS_SRC}' '${KEYBINDINGS_FILE}'"
  echo "            or: bash scripts/setup/new-machine-setup.sh"
else
  # Validate submitPrompt value
  if command -v python3 &>/dev/null; then
    submit_key=$(python3 -c "
import json, sys
try:
    d = json.load(open('${KEYBINDINGS_FILE}'))
    print(d.get('submitPrompt', ''))
except Exception as e:
    print('')
" 2>/dev/null || echo "")
    if [[ "$submit_key" == "ctrl+enter" ]]; then
      _pass "keybindings.json present: submitPrompt=ctrl+enter"
    elif [[ -z "$submit_key" ]]; then
      _warn "keybindings.json present but submitPrompt not set — add: \"submitPrompt\": \"ctrl+enter\""
    else
      _warn "keybindings.json present but submitPrompt=${submit_key} (expected ctrl+enter)"
    fi
  else
    # python3 absent — check with grep
    if grep -q '"submitPrompt".*ctrl+enter' "$KEYBINDINGS_FILE" 2>/dev/null; then
      _pass "keybindings.json present: submitPrompt=ctrl+enter"
    else
      _warn "keybindings.json present but submitPrompt not confirmed as ctrl+enter"
    fi
  fi
fi

# ─────────────────────────────────────────────────────────────────────────────
# UX-2: Screenshot directory reachable and CLAUDE_SCREENSHOT_DIR configured
# Checks: (a) env var set in current shell, OR (b) bashrc-snippets.sh will
# set it on interactive login, AND (c) the default path exists on disk.
# ─────────────────────────────────────────────────────────────────────────────
echo ""
echo "--- Screenshot directory"

# Determine effective screenshot dir — env var takes priority; fall back to
# OS default (same logic bashrc-snippets.sh uses) for nightly/non-interactive runs.
_EFFECTIVE_SCREENSHOT_DIR="${CLAUDE_SCREENSHOT_DIR:-}"
if [[ -z "$_EFFECTIVE_SCREENSHOT_DIR" ]]; then
  if [[ "$WH_OS" == "windows" ]]; then
    _EFFECTIVE_SCREENSHOT_DIR="${USERPROFILE:-$HOME}/Pictures/Screenshots"
  else
    _EFFECTIVE_SCREENSHOT_DIR="${HOME}/Pictures/Screenshots"
  fi
fi

SNIPPET_FILE="${WORKSPACE_HUB}/config/shell/bashrc-snippets.sh"
SHELL_RC="${HOME}/.bashrc"
[[ "$WH_OS" == "windows" ]] && SHELL_RC="${HOME}/.bash_profile"

# Check if snippet is configured (will set CLAUDE_SCREENSHOT_DIR on login)
_SNIPPET_CONFIGURED=false
if [[ -f "$SHELL_RC" ]] && grep -qF "bashrc-snippets" "$SHELL_RC" 2>/dev/null; then
  _SNIPPET_CONFIGURED=true
fi

if [[ -d "$_EFFECTIVE_SCREENSHOT_DIR" ]]; then
  SCREENSHOT_COUNT=$(ls -1 "$_EFFECTIVE_SCREENSHOT_DIR" 2>/dev/null | wc -l || echo "0")
  if [[ -n "${CLAUDE_SCREENSHOT_DIR:-}" ]]; then
    _pass "CLAUDE_SCREENSHOT_DIR=${CLAUDE_SCREENSHOT_DIR} (${SCREENSHOT_COUNT} files)"
  elif [[ "$_SNIPPET_CONFIGURED" == "true" ]]; then
    _pass "screenshot dir ${_EFFECTIVE_SCREENSHOT_DIR} exists; will be set via bashrc-snippets"
  else
    _warn "screenshot dir ${_EFFECTIVE_SCREENSHOT_DIR} exists but CLAUDE_SCREENSHOT_DIR not configured"
    echo "       Fix: source '${SNIPPET_FILE}' from ~/.bashrc"
  fi
else
  _warn "screenshot directory not found: ${_EFFECTIVE_SCREENSHOT_DIR}"
  echo "       Fix: mkdir -p '${_EFFECTIVE_SCREENSHOT_DIR}'"
  echo "            or set CLAUDE_SCREENSHOT_DIR to your actual screenshots path"
fi

# ─────────────────────────────────────────────────────────────────────────────
# UX-3: Chrome Claude extension installed (fcoeoabgfenejglbffodgkkbkcdhcgfn)
# ─────────────────────────────────────────────────────────────────────────────
echo ""
echo "--- Chrome Claude extension"
CLAUDE_EXT_ID="fcoeoabgfenejglbffodgkkbkcdhcgfn"
CHROME_EXT_BASE=""
if [[ "$WH_OS" == "linux" ]]; then
  CHROME_EXT_BASE="${HOME}/.config/google-chrome/Default/Extensions/${CLAUDE_EXT_ID}"
  # Also check Chromium
  if [[ ! -d "$CHROME_EXT_BASE" ]]; then
    CHROME_EXT_BASE="${HOME}/.config/chromium/Default/Extensions/${CLAUDE_EXT_ID}"
  fi
else
  # Windows Git Bash: LOCALAPPDATA in POSIX form
  _WIN_LOCALAPPDATA="${LOCALAPPDATA:-}"
  if [[ -n "$_WIN_LOCALAPPDATA" ]]; then
    _POSIX_LOCALAPPDATA=$(cygpath -u "$_WIN_LOCALAPPDATA" 2>/dev/null || echo "$_WIN_LOCALAPPDATA")
    CHROME_EXT_BASE="${_POSIX_LOCALAPPDATA}/Google/Chrome/User Data/Default/Extensions/${CLAUDE_EXT_ID}"
  fi
fi

if [[ -z "$CHROME_EXT_BASE" || ! -d "$CHROME_EXT_BASE" ]]; then
  _warn "Chrome Claude extension not found (ID: ${CLAUDE_EXT_ID})"
  echo "       Fix: see admin/it/chrome-claude-setup.md"
  echo "       URL: https://chromewebstore.google.com/detail/claude/${CLAUDE_EXT_ID}"
else
  # Find and read manifest for version
  MANIFEST=$(find "$CHROME_EXT_BASE" -name "manifest.json" 2>/dev/null | head -1 || true)
  if [[ -n "$MANIFEST" ]] && command -v python3 &>/dev/null; then
    EXT_VERSION=$(python3 -c "
import json, pathlib
d = json.loads(pathlib.Path('${MANIFEST}').read_text())
print(d.get('version', 'unknown'))
" 2>/dev/null || echo "unknown")
    _pass "Chrome Claude extension installed: version ${EXT_VERSION}"
  else
    _pass "Chrome Claude extension directory present: ${CHROME_EXT_BASE}"
  fi
fi

# ─────────────────────────────────────────────────────────────────────────────
# UX-4: bashrc-snippets.sh sourced (best-effort shell check)
# ─────────────────────────────────────────────────────────────────────────────
echo ""
echo "--- Shell config"
SHELL_RC="${HOME}/.bashrc"
[[ "$WH_OS" == "windows" ]] && SHELL_RC="${HOME}/.bash_profile"

if [[ -f "$SHELL_RC" ]] && grep -qF "bashrc-snippets" "$SHELL_RC" 2>/dev/null; then
  _pass "bashrc-snippets.sh sourced in ${SHELL_RC}"
else
  _warn "bashrc-snippets.sh not sourced in ${SHELL_RC}"
  echo "       Fix: bash '${WORKSPACE_HUB}/scripts/setup/new-machine-setup.sh'"
fi

# ─────────────────────────────────────────────────────────────────────────────
# Summary
# ─────────────────────────────────────────────────────────────────────────────
echo ""
echo "=== UX check: ${PASS} PASS  ${WARN} WARN  ${FAIL} FAIL ==="
if [[ "$FAIL" -gt 0 ]]; then
  echo "    Action required — resolve FAIL items for cross-machine UX consistency."
  [[ "$STRICT" == "true" ]] && exit 1
elif [[ "$WARN" -gt 0 ]]; then
  echo "    Review WARN items — they degrade cross-machine consistency."
else
  echo "    Terminal UX is consistent. No action required."
fi
exit 0
