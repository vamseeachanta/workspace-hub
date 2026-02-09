#!/usr/bin/env bash
# submit-to-gemini.sh — Submit content to Google Gemini CLI for review
# Usage:
#   submit-to-gemini.sh --file <path> --prompt <prompt>
#   submit-to-gemini.sh --commit <sha> [--prompt <prompt>]
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

# Check if gemini CLI is available
if ! command -v gemini &>/dev/null; then
  echo "# Gemini CLI not found"
  echo "# Install: npm install -g @anthropic/gemini or pip install google-generativeai"
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

# Build the content to review
if [[ -n "$COMMIT_SHA" ]]; then
  CONTENT="$(git show --stat "$COMMIT_SHA" 2>/dev/null && echo '---' && git diff "${COMMIT_SHA}~1..${COMMIT_SHA}" 2>/dev/null || echo "Failed to get diff for $COMMIT_SHA")"
else
  CONTENT="$(cat "$CONTENT_FILE")"
fi

# Gemini CLI: -p/--prompt runs non-interactive, stdin is appended to prompt
echo "$CONTENT" | gemini -p "${PROMPT:-Review the following code changes}" -y 2>/dev/null || {
  echo "# Gemini review failed (exit $?)"
  if [[ -n "$COMMIT_SHA" ]]; then
    echo "# Commit: $COMMIT_SHA"
  else
    echo "# File: $CONTENT_FILE"
  fi
}
