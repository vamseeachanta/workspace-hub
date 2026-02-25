#!/usr/bin/env bash
# verify-setup.sh — Post-setup validation for workspace-hub.
# Reports every expected component: PASS / WARN / FAIL with remediation hints.
#
# Usage:
#   bash scripts/setup/verify-setup.sh            # full report (default)
#   bash scripts/setup/verify-setup.sh --strict   # exit 1 if any FAIL
#
# Platform: bash (Linux primary, Windows Git Bash / MINGW64 secondary)
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_HUB="$(cd "${SCRIPT_DIR}/../.." && pwd)"

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

echo "=== workspace-hub verify-setup ==="
echo "    Host: ${HOSTNAME_SHORT}  OS: ${WH_OS}  Date: $(date +%Y-%m-%d)"
echo ""

# ── 1. Git repository ─────────────────────────────────────────────────────────
echo "--- Git"
if git -C "$WORKSPACE_HUB" rev-parse --git-dir &>/dev/null; then
  _pass "workspace-hub is a git repository"
else
  _fail "workspace-hub is not a git repository — clone first"
fi

if git -C "$WORKSPACE_HUB" submodule status --recursive &>/dev/null; then
  UNINITIALIZED=$(git -C "$WORKSPACE_HUB" submodule status --recursive 2>/dev/null \
    | grep -c '^-' || true)
  if [[ "$UNINITIALIZED" -eq 0 ]]; then
    _pass "all submodules initialised"
  else
    _warn "${UNINITIALIZED} submodule(s) not initialised — run: git submodule update --init --recursive"
  fi
else
  _warn "could not check submodule status"
fi

# ── 2. Git hooks ──────────────────────────────────────────────────────────────
echo ""
echo "--- Git hooks"
HOOKS_SRC="${WORKSPACE_HUB}/scripts/hooks"
HOOKS_DST="${WORKSPACE_HUB}/.git/hooks"
for hook in pre-commit post-merge post-rewrite; do
  src="${HOOKS_SRC}/${hook}"
  dst="${HOOKS_DST}/${hook}"
  if [[ ! -f "$src" ]]; then
    _warn "hook source missing: scripts/hooks/${hook}"
  elif [[ ! -f "$dst" ]]; then
    _fail "hook not installed: ${hook} — run: bash scripts/setup/install-all-hooks.sh"
  elif ! cmp -s "$src" "$dst"; then
    _warn "hook out of date: ${hook} — run: bash scripts/setup/install-all-hooks.sh"
  else
    _pass "hook installed and current: ${hook}"
  fi
done

# ── 3. Claude CLI ─────────────────────────────────────────────────────────────
echo ""
echo "--- Claude CLI"
if command -v claude &>/dev/null; then
  CLAUDE_VER=$(claude --version 2>/dev/null | head -1 || echo "unknown")
  _pass "claude CLI found: ${CLAUDE_VER}"
else
  _fail "claude CLI not found — install: npm install -g @anthropic-ai/claude-code"
fi

# ── 4. Other AI CLIs ─────────────────────────────────────────────────────────
echo ""
echo "--- AI CLIs (non-critical)"
for cli in codex gemini; do
  if command -v "$cli" &>/dev/null; then
    _pass "${cli} CLI found"
  else
    _warn "${cli} CLI not found (optional — install if needed)"
  fi
done

# ── 5. Shell aliases ──────────────────────────────────────────────────────────
echo ""
echo "--- Shell aliases"
SNIPPET="${WORKSPACE_HUB}/config/shell/bashrc-snippets.sh"
if [[ -f "$SNIPPET" ]]; then
  _pass "bashrc-snippets.sh exists"
else
  _fail "bashrc-snippets.sh missing: config/shell/bashrc-snippets.sh"
fi
# Check if snippet is sourced (best-effort — may not be active in this shell)
SHELL_RC="${HOME}/.bashrc"
[[ "$WH_OS" == "windows" ]] && SHELL_RC="${HOME}/.bash_profile"
if [[ -f "$SHELL_RC" ]] && grep -qF "bashrc-snippets" "$SHELL_RC" 2>/dev/null; then
  _pass "bashrc-snippets.sh sourced in ${SHELL_RC}"
else
  _warn "bashrc-snippets.sh not sourced in ${SHELL_RC} — run: new-machine-setup.sh to add it"
fi

# ── 6. Claude statusline ──────────────────────────────────────────────────────
echo ""
echo "--- Claude statusline"
CLAUDE_SETTINGS="${HOME}/.claude/settings.json"
if [[ -f "$CLAUDE_SETTINGS" ]] && grep -q "statusBarEnabled" "$CLAUDE_SETTINGS" 2>/dev/null; then
  _pass "statusBarEnabled present in ~/.claude/settings.json"
else
  _warn "statusBarEnabled not found in ~/.claude/settings.json — run: claude config set statusBarEnabled true"
fi

# ── 7. Crontab (Linux only) ───────────────────────────────────────────────────
echo ""
echo "--- Cron"
if [[ "$WH_OS" == "linux" ]]; then
  if crontab -l &>/dev/null; then
    CRON_ENTRIES=$(crontab -l 2>/dev/null | grep -c "workspace-hub" || true)
    if [[ "$CRON_ENTRIES" -gt 0 ]]; then
      _pass "${CRON_ENTRIES} workspace-hub cron entry/entries installed"
    else
      _warn "no workspace-hub entries in crontab — run: bash scripts/cron/setup-cron.sh"
    fi
  else
    _warn "crontab not accessible — run: bash scripts/cron/setup-cron.sh"
  fi
else
  _warn "Windows detected — check Task Scheduler manually (see .claude/docs/new-machine-setup.md)"
fi

# ── 8. SSH key ────────────────────────────────────────────────────────────────
echo ""
echo "--- SSH"
if ls "${HOME}/.ssh/id_"* &>/dev/null; then
  _pass "SSH key found in ~/.ssh/"
else
  _warn "no SSH key found — generate with: ssh-keygen -t ed25519 -C \"\$(hostname)\""
fi

# ── 9. Environment variables ──────────────────────────────────────────────────
echo ""
echo "--- Environment variables"
ENV_EXAMPLE="${WORKSPACE_HUB}/.env.example"
if [[ -f "$ENV_EXAMPLE" ]]; then
  while IFS= read -r line; do
    [[ -z "$line" || "$line" == \#* ]] && continue
    var="${line%%=*}"
    if [[ -n "${!var:-}" ]]; then
      _pass "env var set: ${var}"
    else
      _warn "env var not set: ${var} (see .env.example)"
    fi
  done < "$ENV_EXAMPLE"
else
  _warn ".env.example not found — expected at workspace root"
fi

# ── 9b. Terminal UX consistency (WRK-228) ────────────────────────────────────
echo ""
echo "--- Terminal UX"
KEYBINDINGS_FILE="${HOME}/.claude/keybindings.json"
if [[ ! -f "$KEYBINDINGS_FILE" ]]; then
  _warn "~/.claude/keybindings.json absent — submitPrompt not standardised"
  echo "       Fix: bash ${WORKSPACE_HUB}/scripts/setup/new-machine-setup.sh"
else
  if command -v python3 &>/dev/null; then
    _submit=$(python3 -c "
import json, pathlib
try:
    d=json.loads(pathlib.Path('${KEYBINDINGS_FILE}').read_text())
    print(d.get('submitPrompt',''))
except Exception:
    print('')
" 2>/dev/null || echo "")
    if [[ "$_submit" == "ctrl+enter" ]]; then
      _pass "keybindings.json: submitPrompt=ctrl+enter"
    else
      _warn "keybindings.json: submitPrompt=${_submit:-unset} (expected ctrl+enter)"
    fi
  else
    _pass "keybindings.json present (python3 absent — cannot parse)"
  fi
fi

if [[ -n "${CLAUDE_SCREENSHOT_DIR:-}" ]]; then
  if [[ -d "$CLAUDE_SCREENSHOT_DIR" ]]; then
    _pass "CLAUDE_SCREENSHOT_DIR=${CLAUDE_SCREENSHOT_DIR}"
  else
    _warn "CLAUDE_SCREENSHOT_DIR set but directory missing: ${CLAUDE_SCREENSHOT_DIR}"
  fi
else
  _warn "CLAUDE_SCREENSHOT_DIR not set — source bashrc-snippets.sh or re-open shell"
fi

# ── 10. Python ────────────────────────────────────────────────────────────────
echo ""
echo "--- Python"
if command -v python3 &>/dev/null; then
  PY_VER=$(python3 --version 2>&1 | head -1)
  _pass "python3 found: ${PY_VER}"
  if python3 -c "import yaml" &>/dev/null; then
    _pass "PyYAML available (required for WRK pipeline)"
  else
    _warn "PyYAML not installed — run: pip3 install pyyaml"
  fi
else
  _fail "python3 not found — install Python 3.10+"
fi

# ── Summary ───────────────────────────────────────────────────────────────────
echo ""
echo "=== Summary: ${PASS} PASS  ${WARN} WARN  ${FAIL} FAIL ==="
if [[ "$FAIL" -gt 0 ]]; then
  echo "    Action required: resolve FAIL items before commencing work."
  [[ "$STRICT" == "true" ]] && exit 1
elif [[ "$WARN" -gt 0 ]]; then
  echo "    Review WARN items — they do not block work but affect parity."
else
  echo "    All checks passed. Machine is fully configured."
fi
