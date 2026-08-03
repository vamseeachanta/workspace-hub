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

_codex_version_is_older() {
  local current="$1" pinned="$2"
  local current_major current_minor current_patch pinned_major pinned_minor pinned_patch
  IFS=. read -r current_major current_minor current_patch <<<"$current"
  IFS=. read -r pinned_major pinned_minor pinned_patch <<<"$pinned"
  (( current_major < pinned_major )) && return 0
  (( current_major > pinned_major )) && return 1
  (( current_minor < pinned_minor )) && return 0
  (( current_minor > pinned_minor )) && return 1
  (( current_patch < pinned_patch ))
}

_validate_codex_contract() {
  local template="$1" pinned="$2"
  command -v uv >/dev/null 2>&1 || return 4
  uv run --no-project python - "$template" "$pinned" <<'PY'
import sys
import tomllib
from pathlib import Path

baselines = {
    "0.146.0": {
        "attestation": "# TUI selector attestation: Codex CLI 0.146.0, inspected 2026-08-02.",
        "config": {
            "plan_mode_reasoning_effort": "high",
            "personality": "pragmatic",
            "web_search": "live",
            "features": {
                "default_mode_request_user_input": True,
                "goals": True,
                "multi_agent": True,
                "hooks": True,
            },
            "agents": {"enabled": True, "interrupt_message": True},
            "tui": {
                "resume_cwd": "session",
                "status_line": [
                    "model-with-reasoning", "context-remaining", "current-dir",
                    "five-hour-limit", "weekly-limit",
                ],
            },
        },
    },
}
baseline = baselines.get(sys.argv[2])
if baseline is None:
    raise SystemExit(2)
try:
    text = Path(sys.argv[1]).read_text(encoding="utf-8")
    data = tomllib.loads(text)
except (OSError, tomllib.TOMLDecodeError):
    raise SystemExit(3)
valid = data == baseline["config"] and baseline["attestation"] in text
raise SystemExit(0 if valid else 3)
PY
}

_verify_codex_feature_baseline() {
  local codex_bin="$1" template="$2" candidate_root before after
  candidate_root="$(mktemp -d)" || return 1
  before="$(CODEX_HOME="${candidate_root}/empty" "$codex_bin" features list 2>&1)"
  local before_status=$?
  mkdir -p "${candidate_root}/candidate"
  cp "$template" "${candidate_root}/candidate/config.toml"
  after="$(CODEX_HOME="${candidate_root}/candidate" "$codex_bin" features list 2>&1)"
  local after_status=$?
  rm -rf "$candidate_root"
  if [[ "$before_status" -ne 0 ]]; then
    _fail "codex isolated baseline feature probe failed"
  elif [[ "$after_status" -ne 0 ]]; then
    _fail "codex isolated config load failed"
  elif ! grep -q '^default_mode_request_user_input' <<<"$after"; then
    _fail "codex feature default_mode_request_user_input is absent"
  elif grep -Eq '^default_mode_request_user_input.*false$' <<<"$before" \
    && grep -Eq '^default_mode_request_user_input.*true$' <<<"$after"; then
    _pass "codex feature default_mode_request_user_input: false -> true"
  else
    _fail "codex feature default_mode_request_user_input did not change false -> true"
  fi
}

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
for hook in pre-commit post-merge post-rewrite post-commit; do
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
PIN_ENV="${CODEX_PIN_ENV:-${WORKSPACE_HUB}/scripts/install/codex-pin.env}"
if [[ -f "$PIN_ENV" ]]; then
  # shellcheck source=/dev/null
  source "$PIN_ENV"
else
  CODEX_PIN_VERSION="0.146.0"
fi
for cli in codex gemini; do
  if command -v "$cli" &>/dev/null; then
    if [[ "$cli" == "codex" ]]; then
      CODEX_VER_RAW="$($cli --version 2>/dev/null | head -1 || true)"
      CODEX_VER="$(printf '%s' "$CODEX_VER_RAW" | awk '{print $NF}')"
      if ! [[ "$CODEX_VER" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
        _fail "codex CLI version is malformed: ${CODEX_VER:-empty}"
      elif ! [[ "${CODEX_PIN_VERSION:-}" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
        _fail "codex pin version is malformed: ${CODEX_PIN_VERSION:-empty}"
      elif [[ "$CODEX_VER" == "$CODEX_PIN_VERSION" ]]; then
        _pass "codex CLI found at pinned version ${CODEX_VER}"
        CODEX_TEMPLATE="${CODEX_CONFIG_TEMPLATE:-${WORKSPACE_HUB}/config/agents/codex/config.toml}"
        _validate_codex_contract "$CODEX_TEMPLATE" "$CODEX_PIN_VERSION"
        CODEX_CONTRACT_STATUS=$?
        if [[ "$CODEX_CONTRACT_STATUS" -eq 2 ]]; then
          _fail "no TUI selector attestation for pinned Codex ${CODEX_PIN_VERSION}"
        elif [[ "$CODEX_CONTRACT_STATUS" -eq 4 ]]; then
          _fail "uv is required for Codex canonical config validation"
        else
          _verify_codex_feature_baseline "$cli" "$CODEX_TEMPLATE"
        fi
        case "$CODEX_CONTRACT_STATUS" in
          0)
            _pass "codex TUI footer selectors validated for ${CODEX_PIN_VERSION}"
            _pass "codex canonical config matches owned baseline for ${CODEX_PIN_VERSION}"
            ;;
          2|4) : ;;  # Known failure already reported above.
          3) _fail "codex canonical config does not match owned baseline for ${CODEX_PIN_VERSION}" ;;
          *) _fail "codex canonical config validator failed with status ${CODEX_CONTRACT_STATUS}" ;;
        esac
      elif _codex_version_is_older "$CODEX_VER" "$CODEX_PIN_VERSION"; then
        _fail "codex CLI version ${CODEX_VER} is older than pinned ${CODEX_PIN_VERSION}"
      else
        _fail "codex CLI version drift: ${CODEX_VER:-unknown} (expected ${CODEX_PIN_VERSION}; run scripts/install/pin-codex.sh)"
      fi
    else
      _pass "${cli} CLI found"
    fi
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
if [[ -f "$CLAUDE_SETTINGS" ]] && grep -q "statusBarEnabled\|statusLine" "$CLAUDE_SETTINGS" 2>/dev/null; then
  _pass "statusline configured in ~/.claude/settings.json"
else
  _warn "statusline not configured in ~/.claude/settings.json — run: claude config set statusBarEnabled true"
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
  # Prefer uv (cross-platform, no Windows Store stub issue), fall back to python3
  _py_cmd=""
  if command -v uv &>/dev/null; then
    _py_cmd="uv run --no-project python"
  elif command -v python3 &>/dev/null; then
    _py_cmd="python3"
  fi
  if [[ -n "$_py_cmd" ]]; then
    # Convert POSIX path to native OS path for Python (MINGW64 /c/... → C:\...) # abs-path-allowed
    _kb_native="$KEYBINDINGS_FILE"
    command -v cygpath &>/dev/null && _kb_native="$(cygpath -w "$KEYBINDINGS_FILE" 2>/dev/null || echo "$KEYBINDINGS_FILE")"
    _submit=$($_py_cmd -c "
import json, pathlib
try:
    d=json.loads(pathlib.Path(r'${_kb_native}').read_text())
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
    _pass "keybindings.json present (no python available — cannot parse)"
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
# Prefer uv (cross-platform, avoids Windows Store stub); fall back to python3
_py_bin=""
if command -v uv &>/dev/null; then
  _py_bin="uv run --no-project python"
elif command -v python3 &>/dev/null; then
  _py_bin="python3"
fi
if [[ -n "$_py_bin" ]]; then
  PY_VER=$($_py_bin --version 2>&1 | head -1)
  _pass "python found via ${_py_bin%% *}: ${PY_VER}"
  if $_py_bin -c "import yaml" &>/dev/null; then
    _pass "PyYAML available (required for WRK pipeline)"
  else
    _warn "PyYAML not installed — run: uv tool install pyyaml (or pip3 install pyyaml)"
  fi
else
  _fail "python not found — install uv or Python 3.10+"
  _warn "  uv installer: curl -LsSf https://astral.sh/uv/install.sh | sh"
  _warn "  Windows/MINGW64: add \$USERPROFILE/.local/bin to PATH after install"
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
