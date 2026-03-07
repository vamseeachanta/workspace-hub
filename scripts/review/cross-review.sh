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
WRK_ID=""

# Parse optional args
shift 2
while [[ $# -gt 0 ]]; do
  case "$1" in
    --type)   REVIEW_TYPE="$2"; shift 2 ;;
    --wrk-id) WRK_ID="$2";     shift 2 ;;
    *) echo "Unknown arg: $1" >&2; exit 1 ;;
  esac
done

# Validate review type
case "$REVIEW_TYPE" in
  plan|implementation|commit) ;;
  *) echo "Invalid review type: $REVIEW_TYPE (must be plan, implementation, or commit)" >&2; exit 1 ;;
esac

# --- Stage 5 evidence gate (canonical checker — Phase 1B guard) ----------------
# cross-review.sh is an official Stage 6 entrypoint for plan reviews.
# When --type plan and --wrk-id are supplied, enforce Stage 5 gate.
# Both exit 1 (predicate failure) and exit 2 (infrastructure failure) are fail-closed.
WS_HUB_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
STAGE5_CHECKER="${WS_HUB_ROOT}/scripts/work-queue/verify-gate-evidence.py"
if [[ "$REVIEW_TYPE" == "plan" && -n "$WRK_ID" && -f "$STAGE5_CHECKER" ]]; then
  stage5_exit=0
  stage5_output="$(uv run --no-project python "$STAGE5_CHECKER" \
      --stage5-check "$WRK_ID" 2>&1)" || stage5_exit=$?
  if [[ "$stage5_exit" -eq 1 ]]; then
    echo "✖ Stage 5 evidence gate FAILED (predicate failure) for ${WRK_ID}:" >&2
    echo "$stage5_output" >&2
    echo "Complete Stage 5 interactive review and evidence before Stage 6 cross-review." >&2
    exit 1
  elif [[ "$stage5_exit" -eq 2 ]]; then
    echo "✖ Stage 5 evidence gate FAILED (infrastructure failure) for ${WRK_ID}:" >&2
    echo "$stage5_output" >&2
    echo "Repair the Stage 5 gate infrastructure before proceeding." >&2
    exit 2
  fi
fi

# Determine input mode: file, commit SHA, git range, or inline
CONTENT_FILE=""
COMMIT_SHA=""
SOURCE_NAME=""

sanitize_source_name() {
  local raw="$1"
  # Keep filenames predictable and safe for flat results directory.
  raw="${raw//\//-}"
  raw="${raw// /-}"
  raw="${raw//:/-}"
  raw="${raw//[^A-Za-z0-9._-]/-}"
  raw="$(echo "$raw" | sed -E 's/-+/-/g; s/^-+//; s/-+$//')"
  if [[ -z "$raw" ]]; then
    raw="review-input"
  fi
  echo "$raw"
}

if [[ -f "$FILE_OR_DIFF" ]]; then
  CONTENT_FILE="$FILE_OR_DIFF"
  SOURCE_NAME="$(basename "$FILE_OR_DIFF")"
elif git rev-parse --verify "$FILE_OR_DIFF" &>/dev/null && [[ "$FILE_OR_DIFF" != *".."* ]]; then
  # Valid git commit SHA
  COMMIT_SHA="$(git rev-parse --verify "${FILE_OR_DIFF}^{commit}" 2>/dev/null || true)"
  if [[ -z "$COMMIT_SHA" ]]; then
    echo "ERROR: Invalid commit ref: $FILE_OR_DIFF" >&2
    exit 1
  fi
  SOURCE_NAME="commit-${COMMIT_SHA:0:10}"
elif [[ "$FILE_OR_DIFF" == *".."* ]]; then
  # Git range — write diff to temp file
  CONTENT_FILE="$(mktemp)"
  CLEANUP_FILES+=("$CONTENT_FILE")
  git diff "$FILE_OR_DIFF" > "$CONTENT_FILE" 2>/dev/null || { echo "ERROR: Invalid git range" >&2; exit 1; }
  SOURCE_NAME="git-diff-$(sanitize_source_name "${FILE_OR_DIFF//../-}")"
else
  # Inline content — write to temp file
  CONTENT_FILE="$(mktemp)"
  CLEANUP_FILES+=("$CONTENT_FILE")
  printf '%s\n' "$FILE_OR_DIFF" > "$CONTENT_FILE"
  SOURCE_NAME="inline-content"
fi

# WRK-307: Run Stop hook count guard when reviewing settings.json changes
# Best-effort — warns but does not block the cross-review itself
if [[ -f "${SCRIPT_DIR}/check-stop-hooks.sh" ]]; then
  bash "${SCRIPT_DIR}/check-stop-hooks.sh" || true
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

# Track Codex gate status
CODEX_PASSED=false
CODEX_NO_OUTPUT=false
CODEX_FALLBACK_ALLOWED=false

classify_review_result() {
  local result_file="$1"
  "${SCRIPT_DIR}/validate-review-output.sh" "$result_file" 2>/dev/null || echo "ERROR"
}

preserve_raw_result() {
  local result_file="$1"
  local raw_file="${result_file%.md}.raw.md"
  cp "$result_file" "$raw_file"
}

# Submit to reviewers
submit_review() {
  local reviewer="$1"
  local result_file="${RESULT_PREFIX}-${reviewer}.md"

  echo "--- Submitting to ${reviewer}..."

  case "$reviewer" in
    claude)
      local claude_exit=0
      if [[ -n "$COMMIT_SHA" ]]; then
        "${SCRIPT_DIR}/submit-to-claude.sh" --commit "$COMMIT_SHA" --prompt "$PROMPT" > "$result_file" 2>&1 || claude_exit=$?
      else
        "${SCRIPT_DIR}/submit-to-claude.sh" --file "$CONTENT_FILE" --prompt "$PROMPT" > "$result_file" 2>&1 || claude_exit=$?
      fi
      if [[ "$claude_exit" -eq 124 ]]; then
        # Watchdog timeout — preserve the WATCHDOG log before overwriting result_file
        preserve_raw_result "$result_file"
        echo "# Claude returned NO_OUTPUT (watchdog timeout)" > "$result_file"
      elif [[ "$claude_exit" -ne 0 ]]; then
        echo "# Claude review failed" > "$result_file"
        echo "# Fallback: manual review required" >> "$result_file"
      fi
      local claude_status
      claude_status="$(classify_review_result "$result_file")"
      case "$claude_status" in
        VALID) ;;
        SKIPPED_NETWORK)
          preserve_raw_result "$result_file"
          echo "# Claude returned SKIPPED_NETWORK (DNS failure)" > "$result_file"
          ;;
        NO_OUTPUT)
          preserve_raw_result "$result_file"
          echo "# Claude returned NO_OUTPUT" > "$result_file"
          ;;
        INVALID_OUTPUT)
          echo "    WARNING: Claude returned INVALID_OUTPUT" >&2
          preserve_raw_result "$result_file"
          {
            echo "# Claude returned INVALID_OUTPUT"
            echo "# Output did not match required review format"
          } > "$result_file"
          ;;
        *)
          echo "    WARNING: Claude review classification ERROR" >&2
          ;;
      esac
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
      local codex_status
      codex_status="$(classify_review_result "$result_file")"
      if [[ $codex_exit -eq 0 ]] && [[ "$codex_status" == "VALID" ]] && ! grep -q "^# Codex.*failed\|^# Codex CLI not found\|^# HARD GATE" "$result_file" 2>/dev/null; then
        CODEX_PASSED=true
      elif [[ "$codex_status" == "NO_OUTPUT" ]] && grep -q '^# Codex returned NO_OUTPUT' "$result_file" 2>/dev/null \
          && [[ $codex_exit -eq 0 || $codex_exit -eq 5 ]]; then
        # Fallback only for genuine NO_OUTPUT (empty response from model, exits 0 or 5).
        # Non-zero exits from CLI failures, transport errors, or setup issues are hard gates.
        CODEX_NO_OUTPUT=true
        CODEX_FALLBACK_ALLOWED=true
        echo "    WARNING: Codex returned NO_OUTPUT (${codex_size} bytes, exit $codex_exit) — fallback consensus will be attempted" >&2
      elif [[ $codex_exit -eq 0 && "$codex_status" == "INVALID_OUTPUT" ]]; then
        echo "    WARNING: Codex returned INVALID_OUTPUT — this is a HARD GATE" >&2
        CODEX_NO_OUTPUT=false
        CODEX_FALLBACK_ALLOWED=false
        preserve_raw_result "$result_file"
        {
          echo "# Codex returned INVALID_OUTPUT"
          echo "# HARD GATE: Codex review did not match required format"
        } > "$result_file"
      else
        echo "    WARNING: Codex review FAILED (exit $codex_exit) — this is a HARD GATE" >&2
        preserve_raw_result "$result_file"
        if grep -q "^# Codex CLI not found" "$result_file" 2>/dev/null; then
          CODEX_NO_OUTPUT=false
          CODEX_FALLBACK_ALLOWED=false
          echo "    (Codex CLI missing — fallback disabled; hard gate enforced)" >&2
          echo "# Codex review failed (exit $codex_exit)" > "$result_file"
          echo "# HARD GATE: Codex CLI not found — install Codex and rerun." >> "$result_file"
        elif [[ $codex_exit -ne 0 ]]; then
          CODEX_NO_OUTPUT=false
          CODEX_FALLBACK_ALLOWED=false
          echo "# Codex review failed (exit $codex_exit)" > "$result_file"
          echo "# HARD GATE: Codex review is compulsory — resolve before proceeding" >> "$result_file"
        elif grep -q "^# Codex exec failed\|^# Codex review failed\|^ERROR:" "$result_file" 2>/dev/null; then
          CODEX_NO_OUTPUT=false
          CODEX_FALLBACK_ALLOWED=false
          echo "    (Codex API/model error detected in result — hard gate enforced)" >&2
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
      local gemini_status
      gemini_status="$(classify_review_result "$result_file")"
      case "$gemini_status" in
        VALID) ;;
        SKIPPED_NETWORK)
          preserve_raw_result "$result_file"
          echo "# Gemini returned SKIPPED_NETWORK (DNS failure)" > "$result_file"
          ;;
        NO_OUTPUT)
          preserve_raw_result "$result_file"
          echo "# Gemini returned NO_OUTPUT" > "$result_file"
          ;;
        INVALID_OUTPUT)
          echo "    WARNING: Gemini returned INVALID_OUTPUT" >&2
          preserve_raw_result "$result_file"
          {
            echo "# Gemini returned INVALID_OUTPUT"
            echo "# Output did not match required review format"
          } > "$result_file"
          ;;
        *)
          echo "    WARNING: Gemini review classification ERROR" >&2
          ;;
      esac
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
      if [[ "$CODEX_FALLBACK_ALLOWED" == "true" ]]; then
        echo ""
        echo "--- Codex unavailable/NO_OUTPUT. Attempting 2-of-3 fallback consensus..." >&2
        claude_file="${RESULT_PREFIX}-claude.md"
        gemini_file="${RESULT_PREFIX}-gemini.md"
        claude_status="$(classify_review_result "$claude_file")"
        gemini_status="$(classify_review_result "$gemini_file")"
        claude_verdict="$("${SCRIPT_DIR}/normalize-verdicts.sh" "$claude_file" 2>/dev/null || echo "ERROR")"
        gemini_verdict="$("${SCRIPT_DIR}/normalize-verdicts.sh" "$gemini_file" 2>/dev/null || echo "ERROR")"
        echo "    Claude artifact status: $claude_status" >&2
        echo "    Gemini artifact status: $gemini_status" >&2
        echo "    Claude verdict: $claude_verdict" >&2
        echo "    Gemini verdict: $gemini_verdict" >&2

        if [[ "$claude_status" == "VALID" && "$gemini_status" == "VALID" && \
              ("$claude_verdict" == "APPROVE" || "$claude_verdict" == "MINOR") && \
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
          exit 0
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
