#!/usr/bin/env bash
# submit-to-gemini.sh — Submit content to Google Gemini CLI for review
# Usage: submit-to-gemini.sh <content> <prompt>
set -euo pipefail

CONTENT="${1:?Missing content}"
PROMPT="${2:?Missing prompt}"

# Check if gemini CLI is available
if ! command -v gemini &>/dev/null; then
  echo "# Gemini CLI not found"
  echo "# Install: pip install google-generativeai"
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

# Submit to gemini (pipe mode, non-interactive)
echo "$REVIEW_INPUT" | gemini --quiet 2>/dev/null || {
  echo "# Gemini execution failed"
  echo "# Content saved for manual review"
  echo ""
  echo "$REVIEW_INPUT"
}
