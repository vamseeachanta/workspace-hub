#!/usr/bin/env bash
# cross-review.sh — Unified cross-review submission script
# Submits content to all available AI agents (Claude, Codex, Gemini) for review
# Cross-review is MANDATORY for all plans and implementations per CLAUDE.md
# Usage: cross-review.sh <file_or_diff> <reviewer: claude|codex|gemini|all> [--type plan|implementation|commit]
# Preferred: cross-review.sh <file_or_diff> all --type implementation
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROMPTS_DIR="${SCRIPT_DIR}/prompts"
RESULTS_DIR="${SCRIPT_DIR}/results"
mkdir -p "$RESULTS_DIR"

CLEANUP_FILES=()
cleanup() { for f in "${CLEANUP_FILES[@]}"; do rm -f "$f"; done; }
trap cleanup EXIT

FILE_OR_DIFF="${1:?Usage: cross-review.sh <file_or_diff_or_sha> <reviewer> [--type plan|implementation|commit]}"
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

# Determine input mode: file, commit SHA, git range, or inline
CONTENT_FILE=""
COMMIT_SHA=""
SOURCE_NAME=""

if [[ -f "$FILE_OR_DIFF" ]]; then
  CONTENT_FILE="$FILE_OR_DIFF"
  SOURCE_NAME="$(basename "$FILE_OR_DIFF")"
elif git rev-parse --verify "$FILE_OR_DIFF" &>/dev/null && [[ "$FILE_OR_DIFF" != *".."* ]]; then
  # Valid git commit SHA
  COMMIT_SHA="$FILE_OR_DIFF"
  SOURCE_NAME="commit-${COMMIT_SHA:0:10}"
elif [[ "$FILE_OR_DIFF" == *".."* ]]; then
  # Git range — write diff to temp file
  CONTENT_FILE="$(mktemp)"
  CLEANUP_FILES+=("$CONTENT_FILE")
  git diff "$FILE_OR_DIFF" > "$CONTENT_FILE" 2>/dev/null || { echo "ERROR: Invalid git range" >&2; exit 1; }
  SOURCE_NAME="git-diff-${FILE_OR_DIFF//../-}"
else
  # Inline content — write to temp file
  CONTENT_FILE="$(mktemp)"
  CLEANUP_FILES+=("$CONTENT_FILE")
  echo "$FILE_OR_DIFF" > "$CONTENT_FILE"
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

# Build args for sub-scripts (--file or --commit + --prompt)
build_review_args() {
  local args=()
  if [[ -n "$COMMIT_SHA" ]]; then
    args+=(--commit "$COMMIT_SHA")
  else
    args+=(--file "$CONTENT_FILE")
  fi
  args+=(--prompt "$PROMPT")
  echo "${args[@]}"
}

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
        if [[ -n "$CONTENT_FILE" ]]; then
          head -200 "$CONTENT_FILE"
        else
          echo "Commit: $COMMIT_SHA"
          git show --stat "$COMMIT_SHA" 2>/dev/null | head -50
        fi
        echo '```'
        echo "## Review Prompt"
        echo "$PROMPT"
      } > "$result_file"
      ;;
    codex)
      if [[ -n "$COMMIT_SHA" ]]; then
        "${SCRIPT_DIR}/submit-to-codex.sh" --commit "$COMMIT_SHA" --prompt "$PROMPT" > "$result_file" 2>&1 || {
          echo "# Codex review failed" > "$result_file"
          echo "# Fallback: manual review required" >> "$result_file"
        }
      else
        "${SCRIPT_DIR}/submit-to-codex.sh" --file "$CONTENT_FILE" --prompt "$PROMPT" > "$result_file" 2>&1 || {
          echo "# Codex review failed" > "$result_file"
          echo "# Fallback: manual review required" >> "$result_file"
        }
      fi
      ;;
    gemini)
      if [[ -n "$COMMIT_SHA" ]]; then
        "${SCRIPT_DIR}/submit-to-gemini.sh" --commit "$COMMIT_SHA" --prompt "$PROMPT" > "$result_file" 2>&1 || {
          echo "# Gemini review failed" > "$result_file"
          echo "# Fallback: manual review required" >> "$result_file"
        }
      else
        "${SCRIPT_DIR}/submit-to-gemini.sh" --file "$CONTENT_FILE" --prompt "$PROMPT" > "$result_file" 2>&1 || {
          echo "# Gemini review failed" > "$result_file"
          echo "# Fallback: manual review required" >> "$result_file"
        }
      fi
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
