#!/usr/bin/env bash
# submit-to-codex.sh — Submit content to OpenAI Codex CLI for review
# Usage: submit-to-codex.sh <content> <prompt>
set -euo pipefail

CONTENT="${1:?Missing content}"
PROMPT="${2:?Missing prompt}"

# Check if codex CLI is available
if ! command -v codex &>/dev/null; then
  echo "# Codex CLI not found"
  echo "# Install: npm install -g @openai/codex"
  echo ""
  echo "## Review Prompt"
  echo "$PROMPT"
  echo ""
  echo "## Content to Review"
  echo '```'
  echo "$CONTENT" | head -200
  echo '```'
  exit 0
fi

# Prepare the review request
REVIEW_INPUT="$(cat <<HEREDOC
${PROMPT}

---
CONTENT TO REVIEW:
---

${CONTENT}
HEREDOC
)"

# Submit to codex
# If reviewing a git commit, use codex review --commit
# Otherwise pipe content to codex exec
if [[ "${CODEX_COMMIT_SHA:-}" != "" ]]; then
  codex review --commit "$CODEX_COMMIT_SHA" "$PROMPT" 2>/dev/null || {
    echo "# Codex review --commit failed"
    echo "# Content saved for manual review"
    echo ""
    echo "$REVIEW_INPUT"
  }
else
  echo "$REVIEW_INPUT" | codex exec - 2>/dev/null || {
    echo "# Codex execution failed"
    echo "# Content saved for manual review"
    echo ""
    echo "$REVIEW_INPUT"
  }
fi
