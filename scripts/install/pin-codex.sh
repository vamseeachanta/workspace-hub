#!/usr/bin/env bash
# Pin global OpenAI Codex CLI to the last upstream-confirmed good version (#2479).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=/dev/null
source "${SCRIPT_DIR}/codex-pin.env"
PIN="${CODEX_PIN_VERSION:-0.123.0}"

if ! command -v npm >/dev/null 2>&1; then
  echo "ERROR: npm not found — install Node.js/npm before pinning Codex" >&2
  exit 1
fi

NPM_GLOBAL_BIN="$(npm bin -g 2>/dev/null || true)"
if [[ -z "$NPM_GLOBAL_BIN" ]]; then
  NPM_PREFIX="$(npm config get prefix 2>/dev/null || true)"
  if [[ -n "$NPM_PREFIX" && "$NPM_PREFIX" != "undefined" ]]; then
    NPM_GLOBAL_BIN="${NPM_PREFIX}/bin"
  else
    NPM_GLOBAL_BIN="${HOME}/.npm-global/bin"
  fi
fi

CODEX_BIN="$(command -v codex 2>/dev/null || true)"
if [[ -z "$CODEX_BIN" && -x "${NPM_GLOBAL_BIN}/codex" ]]; then
  CODEX_BIN="${NPM_GLOBAL_BIN}/codex"
fi

cur="<not-installed>"
if [[ -n "$CODEX_BIN" ]]; then
  cur="$($CODEX_BIN --version 2>/dev/null | awk '{print $NF}' || echo '<unknown>')"
fi

if [[ "$cur" == "$PIN" ]]; then
  echo "OK: codex-cli $cur already at pin $PIN"
  exit 0
fi

echo "Installing @openai/codex@${PIN} (was: ${cur}) — pin tracks workspace-hub #2479 / openai/codex#19945"
npm install -g "@openai/codex@${PIN}"

CODEX_BIN="$(command -v codex 2>/dev/null || true)"
if [[ -z "$CODEX_BIN" && -x "${NPM_GLOBAL_BIN}/codex" ]]; then
  CODEX_BIN="${NPM_GLOBAL_BIN}/codex"
fi
if [[ -z "$CODEX_BIN" ]]; then
  echo "ERROR: codex binary not found after npm install (checked PATH and ${NPM_GLOBAL_BIN}/codex)" >&2
  exit 1
fi
new="$($CODEX_BIN --version | awk '{print $NF}')"
if [[ "$new" != "$PIN" ]]; then
  echo "ERROR: install reports $new, expected $PIN" >&2
  exit 1
fi

echo "PINNED: codex-cli $new"
