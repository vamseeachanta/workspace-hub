#!/usr/bin/env bash
# submit-to-claude.sh — Submit content to Claude CLI for review
# Usage:
#   submit-to-claude.sh --file <path> --prompt <prompt>
#   submit-to-claude.sh --commit <sha> [--prompt <prompt>]
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

if ! command -v claude &>/dev/null; then
  echo "# Claude CLI not found"
  echo "# Install: npm install -g @anthropic-ai/claude-code"
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
  exit 0
fi

if [[ -n "$COMMIT_SHA" ]]; then
  CONTENT="$(git show --stat "$COMMIT_SHA" 2>/dev/null && echo '---' && git diff "${COMMIT_SHA}~1..${COMMIT_SHA}" 2>/dev/null || echo "Failed to get diff for $COMMIT_SHA")"
else
  CONTENT="$(cat "$CONTENT_FILE")"
fi

FULL_PROMPT="${PROMPT}

---
CONTENT TO REVIEW:
---

${CONTENT}"

# Protect cross-review pipeline from indefinite hangs in CLI/API.
CLAUDE_TIMEOUT_SECONDS="${CLAUDE_TIMEOUT_SECONDS:-300}"
if command -v timeout >/dev/null 2>&1; then
  timeout "$CLAUDE_TIMEOUT_SECONDS" claude -p "$FULL_PROMPT" 2>/dev/null || {
    echo "# Claude review failed or timed out (exit $?)"
    if [[ -n "$COMMIT_SHA" ]]; then
      echo "# Commit: $COMMIT_SHA"
    else
      echo "# File: $CONTENT_FILE"
    fi
  }
else
  claude -p "$FULL_PROMPT" 2>/dev/null || {
    echo "# Claude review failed (exit $?)"
    if [[ -n "$COMMIT_SHA" ]]; then
      echo "# Commit: $COMMIT_SHA"
    else
      echo "# File: $CONTENT_FILE"
    fi
  }
fi
