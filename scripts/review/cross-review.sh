#!/usr/bin/env bash
# cross-review.sh — Unified cross-review submission script
# Submits content to Claude, Codex, and/or Gemini for review
# Usage: cross-review.sh <file_or_diff> <reviewer: claude|codex|gemini|all> [--type plan|implementation|commit]
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROMPTS_DIR="${SCRIPT_DIR}/prompts"
RESULTS_DIR="${SCRIPT_DIR}/results"
mkdir -p "$RESULTS_DIR"

FILE_OR_DIFF="${1:?Usage: cross-review.sh <file_or_diff> <reviewer> [--type plan|implementation|commit]}"
REVIEWER="${2:?Specify reviewer: claude, codex, gemini, or all}"
REVIEW_TYPE="implementation"

# Parse optional args
shift 2
while [[ $# -gt 0 ]]; do
  case "$1" in
    --type) REVIEW_TYPE="$2"; shift 2 ;;
    *) echo "Unknown arg: $1" >&2; exit 1 ;;
  esac
done

# Validate review type
case "$REVIEW_TYPE" in
  plan|implementation|commit) ;;
  *) echo "Invalid review type: $REVIEW_TYPE (must be plan, implementation, or commit)" >&2; exit 1 ;;
esac

# Get content to review
if [[ -f "$FILE_OR_DIFF" ]]; then
  CONTENT="$(cat "$FILE_OR_DIFF")"
  SOURCE_NAME="$(basename "$FILE_OR_DIFF")"
elif [[ "$FILE_OR_DIFF" == *".."* ]]; then
  # Treat as git commit range
  CONTENT="$(git diff "$FILE_OR_DIFF" 2>/dev/null || { echo "ERROR: Invalid git range" >&2; exit 1; })"
  SOURCE_NAME="git-diff-${FILE_OR_DIFF//../-}"
else
  CONTENT="$FILE_OR_DIFF"
  SOURCE_NAME="inline-content"
fi

# Load prompt template
PROMPT_FILE="${PROMPTS_DIR}/${REVIEW_TYPE}-review.md"
if [[ ! -f "$PROMPT_FILE" ]]; then
  echo "ERROR: Missing prompt template: $PROMPT_FILE" >&2
  exit 1
fi

PROMPT="$(cat "$PROMPT_FILE")"
TIMESTAMP="$(date -u +%Y%m%dT%H%M%SZ)"
RESULT_PREFIX="${RESULTS_DIR}/${TIMESTAMP}-${SOURCE_NAME}-${REVIEW_TYPE}"

# Submit to reviewers
submit_review() {
  local reviewer="$1"
  local result_file="${RESULT_PREFIX}-${reviewer}.md"

  echo "--- Submitting to ${reviewer}..."

  case "$reviewer" in
    claude)
      {
        echo "# Review by Claude"
        echo "# Source: ${SOURCE_NAME}"
        echo "# Type: ${REVIEW_TYPE}"
        echo "# Date: ${TIMESTAMP}"
        echo ""
        echo "[Claude review requires interactive session or API call]"
        echo "## Content to Review"
        echo '```'
        echo "$CONTENT" | head -200
        echo '```'
        echo "## Review Prompt"
        echo "$PROMPT"
      } > "$result_file"
      ;;
    codex)
      "${SCRIPT_DIR}/submit-to-codex.sh" "$CONTENT" "$PROMPT" > "$result_file" 2>&1 || {
        echo "# Codex review failed" > "$result_file"
        echo "# Fallback: manual review required" >> "$result_file"
      }
      ;;
    gemini)
      "${SCRIPT_DIR}/submit-to-gemini.sh" "$CONTENT" "$PROMPT" > "$result_file" 2>&1 || {
        echo "# Gemini review failed" > "$result_file"
        echo "# Fallback: manual review required" >> "$result_file"
      }
      ;;
  esac

  echo "    Result: ${result_file}"
}

# Dispatch
case "$REVIEWER" in
  all)
    submit_review "claude"
    submit_review "codex"
    submit_review "gemini"
    echo "--- All reviews submitted. Results in: ${RESULTS_DIR}/"
    ;;
  claude|codex|gemini)
    submit_review "$REVIEWER"
    ;;
  *)
    echo "Unknown reviewer: $REVIEWER (must be claude, codex, gemini, or all)" >&2
    exit 1
    ;;
esac
