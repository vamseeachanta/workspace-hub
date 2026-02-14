#!/usr/bin/env bash
# submit-to-codex.sh — Submit content to OpenAI Codex CLI for review
# Usage:
#   submit-to-codex.sh --file <path> --prompt <prompt>
#   submit-to-codex.sh --commit <sha> [--prompt <prompt>]
set -euo pipefail

CONTENT_FILE=""
COMMIT_SHA=""
PROMPT=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --file)   CONTENT_FILE="$2"; shift 2 ;;
    --commit) COMMIT_SHA="$2"; shift 2 ;;
    --prompt) PROMPT="$2"; shift 2 ;;
    *) echo "Unknown arg: $1" >&2; exit 1 ;;
  esac
done

if [[ -z "$COMMIT_SHA" && -z "$CONTENT_FILE" ]]; then
  echo "ERROR: Provide --file <path> or --commit <sha>" >&2
  exit 1
fi

# Check if codex CLI is available
if ! command -v codex &>/dev/null; then
  echo "# Codex CLI not found"
  echo "# Install: npm install -g @openai/codex"
  echo "# CODEX REVIEW IS COMPULSORY — install the CLI and retry"
  echo ""
  echo "## Review Prompt"
  echo "$PROMPT"
  echo ""
  echo "## Content to Review"
  echo '```'
  if [[ -n "$CONTENT_FILE" ]]; then
    head -200 "$CONTENT_FILE"
  else
    echo "Commit: $COMMIT_SHA"
  fi
  echo '```'
  exit 2
fi

if [[ -n "$COMMIT_SHA" ]]; then
  # Review a specific git commit
  # codex review --commit <SHA> cannot be combined with positional PROMPT.
  # Codex writes review output to stderr, so capture both streams.
  codex review --commit "$COMMIT_SHA" 2>&1 || {
    echo "# Codex review --commit failed (exit $?)"
    echo "# Commit: $COMMIT_SHA"
  }
else
  # Review file content via codex exec (pipe content + prompt via stdin)
  FULL_PROMPT="${PROMPT}

---
CONTENT TO REVIEW:
---

$(cat "$CONTENT_FILE")"

  echo "$FULL_PROMPT" | codex exec - 2>&1 || {
    echo "# Codex exec failed (exit $?)"
    echo "# File: $CONTENT_FILE"
  }
fi
