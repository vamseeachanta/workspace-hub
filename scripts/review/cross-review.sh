#!/usr/bin/env bash
# cross-review.sh — Unified cross-review submission script
# Submits content to all available AI agents (Claude, Codex, Gemini) for review
# Cross-review is MANDATORY for all plans and implementations per CLAUDE.md
# CODEX IS A HARD GATE — script exits non-zero if Codex review fails
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

# Track Codex gate status
CODEX_PASSED=false
CODEX_NO_OUTPUT=false

# Submit to reviewers
submit_review() {
  local reviewer="$1"
  local result_file="${RESULT_PREFIX}-${reviewer}.md"

  echo "--- Submitting to ${reviewer}..."

  case "$reviewer" in
    claude)
      if [[ -n "$COMMIT_SHA" ]]; then
        "${SCRIPT_DIR}/submit-to-claude.sh" --commit "$COMMIT_SHA" --prompt "$PROMPT" > "$result_file" 2>&1 || {
          echo "# Claude review failed" > "$result_file"
          echo "# Fallback: manual review required" >> "$result_file"
        }
      else
        "${SCRIPT_DIR}/submit-to-claude.sh" --file "$CONTENT_FILE" --prompt "$PROMPT" > "$result_file" 2>&1 || {
          echo "# Claude review failed" > "$result_file"
          echo "# Fallback: manual review required" >> "$result_file"
        }
      fi
      ;;
    codex)
      local codex_exit=0
      if [[ -n "$COMMIT_SHA" ]]; then
        "${SCRIPT_DIR}/submit-to-codex.sh" --commit "$COMMIT_SHA" --prompt "$PROMPT" > "$result_file" 2>&1 || codex_exit=$?
      else
        "${SCRIPT_DIR}/submit-to-codex.sh" --file "$CONTENT_FILE" --prompt "$PROMPT" > "$result_file" 2>&1 || codex_exit=$?
      fi
      # Check if Codex produced a real verdict (not just a failure stub)
      # A real Codex review contains "codex" output lines (the model's response)
      local codex_size=0
      [[ -f "$result_file" ]] && codex_size="$(wc -c < "$result_file" | tr -d ' ')"
      if [[ $codex_exit -eq 0 ]] && ! grep -q "^# Codex.*failed\|^# Codex CLI not found\|^# HARD GATE" "$result_file" 2>/dev/null && grep -q "^codex$" "$result_file" 2>/dev/null; then
        CODEX_PASSED=true
      elif [[ $codex_exit -eq 0 && "$codex_size" -lt 10 ]]; then
        # Codex ran but produced empty/trivial output (known large-diff limitation)
        CODEX_NO_OUTPUT=true
        echo "    WARNING: Codex returned NO_OUTPUT (${codex_size} bytes) — fallback consensus will be attempted" >&2
        echo "# Codex returned NO_OUTPUT (empty response on large diff)" > "$result_file"
      else
        echo "    WARNING: Codex review FAILED (exit $codex_exit) — this is a HARD GATE" >&2
        if [[ $codex_exit -ne 0 ]]; then
          CODEX_NO_OUTPUT=true
          echo "# Codex review failed (exit $codex_exit)" > "$result_file"
          echo "# HARD GATE: Codex review is compulsory — resolve before proceeding" >> "$result_file"
        fi
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
    if [[ "$CODEX_PASSED" != "true" ]]; then
      # WRK-160: Codex fallback — attempt 2-of-3 consensus when Codex returns NO_OUTPUT
      if [[ "$CODEX_NO_OUTPUT" == "true" ]]; then
        echo ""
        echo "--- Codex returned NO_OUTPUT. Attempting 2-of-3 fallback consensus..." >&2
        local claude_verdict gemini_verdict
        claude_file="${RESULT_PREFIX}-claude.md"
        gemini_file="${RESULT_PREFIX}-gemini.md"
        claude_verdict="$("${SCRIPT_DIR}/normalize-verdicts.sh" "$claude_file" 2>/dev/null || echo "ERROR")"
        gemini_verdict="$("${SCRIPT_DIR}/normalize-verdicts.sh" "$gemini_file" 2>/dev/null || echo "ERROR")"
        echo "    Claude verdict: $claude_verdict" >&2
        echo "    Gemini verdict: $gemini_verdict" >&2

        if [[ ("$claude_verdict" == "APPROVE" || "$claude_verdict" == "MINOR") && \
              ("$gemini_verdict" == "APPROVE" || "$gemini_verdict" == "MINOR") ]]; then
          echo "=== CODEX FALLBACK: 2-of-3 consensus reached (Claude=$claude_verdict, Gemini=$gemini_verdict) ===" >&2
          # Write fallback result
          fallback_file="${RESULT_PREFIX}-FALLBACK.md"
          cat > "$fallback_file" <<FALLBACK_EOF
# Codex Fallback Consensus (WRK-160)
- **Codex**: NO_OUTPUT (empty response)
- **Claude**: $claude_verdict
- **Gemini**: $gemini_verdict
- **Result**: CONDITIONAL_PASS (2-of-3 consensus)
- **Timestamp**: $(date -u +%Y-%m-%dT%H:%M:%SZ)
- **Policy**: Codex remains primary authority; fallback only on NO_OUTPUT, never on explicit REJECT/MAJOR
FALLBACK_EOF
          echo "    Fallback result: $fallback_file" >&2
          # Exit 0 — conditional pass
        else
          echo "=== CODEX HARD GATE FAILED (no fallback consensus) ===" >&2
          echo "Claude=$claude_verdict, Gemini=$gemini_verdict — need both APPROVE or MINOR for fallback." >&2
          echo "Review results saved to: ${RESULTS_DIR}/" >&2
          exit 1
        fi
      else
        echo ""
        echo "=== CODEX HARD GATE FAILED ===" >&2
        echo "Codex review is compulsory per workspace policy." >&2
        echo "Install Codex CLI (npm install -g @openai/codex) or resolve the failure before proceeding." >&2
        echo "Review results saved to: ${RESULTS_DIR}/" >&2
        exit 1
      fi
    fi
    ;;
  codex)
    submit_review "codex"
    if [[ "$CODEX_PASSED" != "true" ]]; then
      echo "=== CODEX HARD GATE FAILED ===" >&2
      exit 1
    fi
    ;;
  claude|gemini)
    submit_review "$REVIEWER"
    ;;
  *)
    echo "Unknown reviewer: $REVIEWER (must be claude, codex, gemini, or all)" >&2
    exit 1
    ;;
esac
