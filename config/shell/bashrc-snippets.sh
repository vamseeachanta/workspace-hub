#!/usr/bin/env bash
# bashrc-snippets.sh — Shared shell aliases + prompt for workspace-hub.
# Source this file from ~/.bashrc or ~/.bash_profile.
#
# Usage (add one line to ~/.bashrc):
#   source /path/to/workspace-hub/config/shell/bashrc-snippets.sh
#
# Or let new-machine-setup.sh append it automatically.
#
# Platform: bash (Linux primary, Windows Git Bash / MINGW64 secondary)
# DO NOT run directly — source only.

# ── Detect platform ───────────────────────────────────────────────────────────
_WH_OS="linux"
case "$(uname -s 2>/dev/null)" in
  MINGW*|CYGWIN*|MSYS*) _WH_OS="windows" ;;
esac

# ── Workspace root ────────────────────────────────────────────────────────────
# Resolve the real workspace root from this file's own location so the snippet
# stays correct after moves/renames.
_WH_SNIPPET_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" 2>/dev/null && pwd)"
WORKSPACE_HUB="$(cd "${_WH_SNIPPET_DIR}/../.." 2>/dev/null && pwd)"
export WORKSPACE_HUB

# ── Screenshot directory (WRK-228) ───────────────────────────────────────────
# Set CLAUDE_SCREENSHOT_DIR so Claude Code can locate screenshots without
# manual navigation. Override by setting the var before sourcing this file.
if [[ -z "${CLAUDE_SCREENSHOT_DIR:-}" ]]; then
  if [[ "$_WH_OS" == "windows" ]]; then
    # Windows Git Bash: USERPROFILE is the Windows home dir
    _WH_WIN_PICS="${USERPROFILE:-$HOME}/Pictures/Screenshots"
    # Normalise Windows path to POSIX form for bash
    _WH_WIN_PICS_POSIX=$(cygpath -u "$_WH_WIN_PICS" 2>/dev/null || echo "$_WH_WIN_PICS")
    export CLAUDE_SCREENSHOT_DIR="$_WH_WIN_PICS_POSIX"
  else
    # Linux: GNOME default screenshot location
    export CLAUDE_SCREENSHOT_DIR="${HOME}/Pictures/Screenshots"
  fi
fi

# ── PATH entries ──────────────────────────────────────────────────────────────
# Node/npm global bin (claude, codex CLIs installed here)
if [[ "$_WH_OS" == "linux" ]]; then
  _NPM_BIN="${HOME}/.npm-global/bin"
  [[ -d "$_NPM_BIN" ]] && export PATH="${_NPM_BIN}:${PATH}"
fi

# Python user bin (pip --user installs land here)
if [[ "$_WH_OS" == "linux" ]]; then
  _PY_USER_BIN="${HOME}/.local/bin"
  [[ -d "$_PY_USER_BIN" ]] && export PATH="${_PY_USER_BIN}:${PATH}"
fi

# ── Core aliases ──────────────────────────────────────────────────────────────
# Quick jump to workspace root
alias ws='cd "${WORKSPACE_HUB}"'

# Work-queue status
alias wrk='bash "${WORKSPACE_HUB}/scripts/work-queue/queue-status.sh"'

# Verify this machine's setup health
alias wh-verify='bash "${WORKSPACE_HUB}/scripts/setup/verify-setup.sh"'

# Run legal scan (diff-only, fast)
alias wh-legal='bash "${WORKSPACE_HUB}/scripts/legal/legal-sanity-scan.sh" --diff-only'

# Open nightly readiness check
alias wh-ready='bash "${WORKSPACE_HUB}/scripts/readiness/nightly-readiness.sh"'

# UX consistency check (keybindings, screenshot dir, Chrome extension)
alias wh-ux='bash "${WORKSPACE_HUB}/scripts/readiness/check-ux-consistency.sh"'

# ── Shell prompt: branch + active WRK item ────────────────────────────────────
# Appended to PS1; only activates inside a git repo.
_wh_prompt_info() {
  local branch wrk_item
  branch="$(git rev-parse --abbrev-ref HEAD 2>/dev/null)" || return
  wrk_item="$(git log --oneline -1 2>/dev/null | grep -oE 'WRK-[0-9]+' | head -1 || true)"
  if [[ -n "$wrk_item" ]]; then
    printf ' \e[36m(%s|%s)\e[0m' "$branch" "$wrk_item"
  else
    printf ' \e[36m(%s)\e[0m' "$branch"
  fi
}

# Only modify PS1 if it is not already customised by another tool (starship, oh-my-bash, etc.)
if [[ -z "${STARSHIP_SESSION_KEY:-}" ]] && [[ -z "${OH_MY_BASH:-}" ]]; then
  PS1='\u@\h:\w$(_wh_prompt_info)\$ '
fi

# ── Windows Git Bash extras ───────────────────────────────────────────────────
if [[ "$_WH_OS" == "windows" ]]; then
  # Ensure LF line endings for all new files created in this shell
  export GIT_CONFIG_PARAMETERS="'core.autocrlf=input'"

  # Windows workspace path alias (adjust drive letter if needed)
  # alias ws='cd /d/workspace-hub'  # uncomment and set correct path
fi
