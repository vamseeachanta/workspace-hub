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

# Submit to codex (pipe mode, non-interactive)
echo "$REVIEW_INPUT" | codex --quiet 2>/dev/null || {
  echo "# Codex execution failed"
  echo "# Content saved for manual review"
  echo ""
  echo "$REVIEW_INPUT"
}
