#!/usr/bin/env bash
# submit-to-codex.sh — Submit content to OpenAI Codex CLI for review
# Usage:
#   submit-to-codex.sh --file <path> --prompt <prompt>
#   submit-to-codex.sh --commit <sha> [--prompt <prompt>]
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
RENDERER="${SCRIPT_DIR}/render-structured-review.py"
VALIDATOR="${SCRIPT_DIR}/validate-review-output.sh"

CONTENT_FILE=""
COMMIT_SHA=""
PROMPT=""
WRK_ID=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --file)   CONTENT_FILE="$2"; shift 2 ;;
    --commit) COMMIT_SHA="$2"; shift 2 ;;
    --prompt) PROMPT="$2"; shift 2 ;;
    *) echo "Unknown arg: $1" >&2; exit 1 ;;
  esac
done

if [[ -n "$CONTENT_FILE" ]]; then
  if [[ "$CONTENT_FILE" =~ (WRK-[0-9]+) ]]; then
    WRK_ID="${BASH_REMATCH[1]}"
  fi
fi

if [[ -z "$COMMIT_SHA" && -z "$CONTENT_FILE" ]]; then
  echo "ERROR: Provide --file <path> or --commit <sha>" >&2
  exit 1
fi

# Check if codex CLI is available (also check npm global bin)
CODEX_BIN="codex"
if ! command -v codex &>/dev/null; then
  if [[ -x "${HOME}/.npm-global/bin/codex" ]]; then
    CODEX_BIN="${HOME}/.npm-global/bin/codex"
  fi
fi
if ! command -v "$CODEX_BIN" &>/dev/null && [[ ! -x "$CODEX_BIN" ]]; then
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
  "$CODEX_BIN" review --commit "$COMMIT_SHA" 2>&1 || {
    echo "# Codex review --commit failed (exit $?)"
    echo "# Commit: $COMMIT_SHA"
  }
else
  # Review file content via codex exec using output-schema + output-last-message
  SCOPE_PREFIX=""
  if [[ -n "$WRK_ID" ]]; then
    SCOPE_PREFIX="WRK in scope: ${WRK_ID}
This review is being run under the active approved work item above.

"
  fi

  FULL_PROMPT="${SCOPE_PREFIX}${PROMPT}

---
CONTENT TO REVIEW:
---

$(cat "$CONTENT_FILE")"

  schema_file="$(mktemp)"
  raw_file="$(mktemp)"
  rendered_file="$(mktemp)"
  trap 'rm -f "$schema_file" "$raw_file" "$rendered_file"' EXIT

  cat > "$schema_file" <<'EOF'
{
  "type": "object",
  "properties": {
    "verdict": { "type": "string" },
    "summary": { "type": "string" },
    "issues_found": { "type": "array", "items": { "type": "string" } },
    "suggestions": { "type": "array", "items": { "type": "string" } },
    "questions_for_author": { "type": "array", "items": { "type": "string" } }
  },
  "required": ["verdict", "summary", "issues_found", "suggestions", "questions_for_author"],
  "additionalProperties": false
}
EOF

  "$CODEX_BIN" exec "$FULL_PROMPT" \
    --skip-git-repo-check \
    --output-schema "$schema_file" \
    --output-last-message "$raw_file" >/dev/null 2>&1 || {
      echo "# Codex exec failed (exit $?)"
      echo "# File: $CONTENT_FILE"
      exit 0
    }

  if python3 "$RENDERER" --provider codex --input "$raw_file" > "$rendered_file" 2>/dev/null \
    && [[ "$("$VALIDATOR" "$rendered_file")" == "VALID" ]]; then
    cat "$rendered_file"
  else
    if [[ -s "$raw_file" ]]; then
      cat "$raw_file"
    else
      echo "# Codex returned NO_OUTPUT"
    fi
  fi
fi
