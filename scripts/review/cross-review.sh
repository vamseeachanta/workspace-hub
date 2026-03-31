#!/usr/bin/env bash
# cross-review.sh — Unified cross-review submission script
# Submits content to all available AI agents (Claude, Codex, Gemini) for review
# Cross-review is MANDATORY for all plans and implementations per CLAUDE.md
# CODEX IS A HARD GATE — script exits non-zero if Codex review fails
# Usage: cross-review.sh <file_or_diff> <reviewer: claude|codex|gemini|all> [--type plan|implementation|commit]
# Preferred: cross-review.sh <file_or_diff> all --type implementation
set -euo pipefail

MAX_REVIEW_ITERATIONS=3

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
ALLOW_NO_CODEX=false
shift 2
while [[ $# -gt 0 ]]; do
  case "$1" in
    --type)          REVIEW_TYPE="$2"; shift 2 ;;
    --wrk-id)        WRK_ID="$2";     shift 2 ;;
    --allow-no-codex) ALLOW_NO_CODEX=true; shift ;;
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
# WRK-5124: Added uv pre-check, timeout wrapper, gtimeout fallback.
WS_HUB_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
STAGE5_CHECKER="${WS_HUB_ROOT}/scripts/work-queue/verify-gate-evidence.py"
if [[ "$REVIEW_TYPE" == "plan" && -n "$WRK_ID" ]]; then
  if [[ ! -f "$STAGE5_CHECKER" ]]; then
    echo "✖ Stage 5 checker not found: ${STAGE5_CHECKER}" >&2
    echo "Repair the Stage 5 gate infrastructure before proceeding." >&2
    exit 2
  fi

  # Pre-check: uv must be available
  if ! command -v uv >/dev/null 2>&1; then
    echo "✖ uv not found — required for Stage 5 gate check" >&2
    exit 2
  fi

  # Resolve timeout command: timeout → gtimeout → none (with warning)
  _TIMEOUT_CMD=""
  if command -v timeout >/dev/null 2>&1; then
    _TIMEOUT_CMD="timeout"
  elif command -v gtimeout >/dev/null 2>&1; then
    _TIMEOUT_CMD="gtimeout"
  else
    echo "⚠ Neither timeout nor gtimeout found — running gate check without timeout guard" >&2
  fi

  # Read checker_timeout from gate config (default 30s, validate as positive integer)
  GATE_CONFIG="${WS_HUB_ROOT}/scripts/work-queue/stage5-gate-config.yaml"
  checker_timeout=$(grep -m1 'checker_timeout:' "$GATE_CONFIG" 2>/dev/null | awk '{print $2}')
  if ! [[ "${checker_timeout:-}" =~ ^[1-9][0-9]*$ ]]; then
    checker_timeout=30
  fi

  # Run gate check with timeout guard (or without if no timeout command)
  stage5_exit=0
  if [[ -n "$_TIMEOUT_CMD" ]]; then
    stage5_output="$($_TIMEOUT_CMD "${checker_timeout}s" uv run --no-project python "$STAGE5_CHECKER" \
        --stage5-check "$WRK_ID" 2>&1)" || stage5_exit=$?
  else
    stage5_output="$(uv run --no-project python "$STAGE5_CHECKER" \
        --stage5-check "$WRK_ID" 2>&1)" || stage5_exit=$?
  fi

  # Handle exit codes: 124=timeout, 1=predicate failure, other=infrastructure failure
  if [[ "$stage5_exit" -eq 124 ]]; then
    echo "✖ Stage 5 gate check TIMED OUT after ${checker_timeout}s for ${WRK_ID}" >&2
    echo "Check uv environment and verify-gate-evidence.py availability." >&2
    exit 2
  elif [[ "$stage5_exit" -eq 1 ]]; then
    echo "✖ Stage 5 evidence gate FAILED (predicate failure) for ${WRK_ID}:" >&2
    echo "$stage5_output" >&2
    echo "Complete Stage 5 interactive review and evidence before Stage 6 cross-review." >&2
    exit 1
  elif [[ "$stage5_exit" -eq 2 ]] || [[ "$stage5_exit" -ne 0 ]]; then
    echo "✖ Stage 5 evidence gate FAILED (infrastructure failure, exit $stage5_exit) for ${WRK_ID}:" >&2
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

# Auto-extract WRK_ID from file path or source name when not supplied via --wrk-id
if [[ -z "$WRK_ID" && "$FILE_OR_DIFF" =~ [Ww][Rr][Kk]-([0-9]+) ]]; then
  WRK_ID="WRK-${BASH_REMATCH[1]}"
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
CODEX_CLI_MISSING=false
CODEX_QUOTA_EXHAUSTED=false
CODEX_OPUS_FALLBACK=false
# Max Codex reviews per WRK before auto-switching to Opus (saves quota)
CODEX_MAX_REVIEWS_PER_WRK="${CODEX_MAX_REVIEWS_PER_WRK:-2}"
# Opus model used as Codex substitute when quota exhausted or limit reached
CODEX_OPUS_MODEL="${CODEX_OPUS_MODEL:-claude-opus-4-6}"

classify_review_result() {
  local result_file="$1"
  "${SCRIPT_DIR}/validate-review-output.sh" "$result_file" 2>/dev/null || echo "ERROR"
}

# Count existing Codex review files for a given WRK (looks at RESULTS_DIR)
count_wrk_codex_reviews() {
  local wrk_id_lower
  wrk_id_lower="$(echo "${WRK_ID:-}" | tr '[:upper:]' '[:lower:]' | tr '-' '-')"
  if [[ -z "$wrk_id_lower" ]]; then
    echo 0; return
  fi
  ls "$RESULTS_DIR"/*"${wrk_id_lower}"*-codex.md 2>/dev/null | grep -v "opus-fallback" | wc -l | tr -d ' '
}

# Run Claude Opus as a substitute for Codex; writes verdict to result_file
run_opus_as_codex_sub() {
  local result_file="$1"
  local opus_exit=0
  local header="# Codex-slot: Claude Opus fallback (${CODEX_OPUS_MODEL})\n"
  if [[ -n "$COMMIT_SHA" ]]; then
    CLAUDE_MODEL="$CODEX_OPUS_MODEL" "${SCRIPT_DIR}/submit-to-claude.sh" \
      --commit "$COMMIT_SHA" --prompt "$PROMPT" > "$result_file" 2>&1 || opus_exit=$?
  else
    CLAUDE_MODEL="$CODEX_OPUS_MODEL" "${SCRIPT_DIR}/submit-to-claude.sh" \
      --file "$CONTENT_FILE" --prompt "$PROMPT" > "$result_file" 2>&1 || opus_exit=$?
  fi
  # Prepend fallback header without overwriting the verdict body
  local tmp_body
  tmp_body="$(cat "$result_file")"
  printf '%b\n%s\n' "$header" "$tmp_body" > "$result_file"
  return "$opus_exit"
}

preserve_raw_result() {
  local result_file="$1"
  local raw_file="${result_file%.md}.raw.md"
  cp "$result_file" "$raw_file"
}

# Returns the current iteration number (1-based) for the given WRK, initialising if absent.
get_review_iteration() {
  local wrk_id="$1"
  local iter_file="${WS_HUB_ROOT}/.claude/work-queue/assets/${wrk_id}/review-iteration.yaml"
  if [[ ! -f "$iter_file" ]]; then echo 0; return; fi
  awk -F': ' '/^iteration:/ {print $2+0; exit}' "$iter_file"
}

# Increments iteration counter; writes review-iteration.yaml; returns new count.
increment_review_iteration() {
  local wrk_id="$1"
  local assets_dir="${WS_HUB_ROOT}/.claude/work-queue/assets/${wrk_id}"
  mkdir -p "$assets_dir"
  local iter_file="${assets_dir}/review-iteration.yaml"
  local current; current="$(get_review_iteration "$wrk_id")"
  local new_count=$(( current + 1 ))
  local first_review_at
  first_review_at="$(awk -F': ' '/^first_review_at:/ {print $2; exit}' "$iter_file" 2>/dev/null \
    || date -u +%Y-%m-%dT%H:%M:%SZ)"
  cat > "$iter_file" <<YAML
wrk_id: "${wrk_id}"
iteration: ${new_count}
first_review_at: "${first_review_at}"
last_review_at: "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
YAML
  echo "$new_count"
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
      # Check if WRK has already reached the Codex review limit → use Opus automatically
      local existing_codex_count
      existing_codex_count="$(count_wrk_codex_reviews)"
      if [[ "$existing_codex_count" -ge "$CODEX_MAX_REVIEWS_PER_WRK" ]]; then
        echo "    INFO: Codex review limit reached (${existing_codex_count}/${CODEX_MAX_REVIEWS_PER_WRK} for ${WRK_ID:-this WRK}) — using Claude Opus (${CODEX_OPUS_MODEL})" >&2
        CODEX_OPUS_FALLBACK=true
        local opus_exit=0
        run_opus_as_codex_sub "$result_file" || opus_exit=$?
        local opus_status
        opus_status="$(classify_review_result "$result_file")"
        if [[ "$opus_status" == "VALID" ]]; then
          CODEX_PASSED=true
        fi
        echo "    Result (Opus sub): ${result_file}"
        return
      fi

      local codex_exit=0
      if [[ -n "$COMMIT_SHA" ]]; then
        "${SCRIPT_DIR}/submit-to-codex.sh" --commit "$COMMIT_SHA" --prompt "$PROMPT" > "$result_file" 2>&1 || codex_exit=$?
      else
        "${SCRIPT_DIR}/submit-to-codex.sh" --file "$CONTENT_FILE" --prompt "$PROMPT" > "$result_file" 2>&1 || codex_exit=$?
      fi
      # Quota exhaustion (exit 3) → automatic Opus fallback
      if [[ $codex_exit -eq 3 ]] || grep -q "^# CODEX_QUOTA_EXHAUSTED" "$result_file" 2>/dev/null; then
        echo "    INFO: Codex quota exhausted — falling back to Claude Opus (${CODEX_OPUS_MODEL})" >&2
        CODEX_QUOTA_EXHAUSTED=true
        CODEX_OPUS_FALLBACK=true
        local opus_exit=0
        run_opus_as_codex_sub "$result_file" || opus_exit=$?
        local opus_status
        opus_status="$(classify_review_result "$result_file")"
        if [[ "$opus_status" == "VALID" ]]; then
          CODEX_PASSED=true
        fi
        echo "    Result (Opus fallback): ${result_file}"
        return
      fi
      # Check if Codex produced a real verdict (not just a failure stub)
      local codex_size=0
      [[ -f "$result_file" ]] && codex_size="$(wc -c < "$result_file" | tr -d ' ')"
      local codex_status
      codex_status="$(classify_review_result "$result_file")"
      if [[ $codex_exit -eq 0 ]] && [[ "$codex_status" == "VALID" ]] && ! grep -q "^# Codex.*failed\|^# Codex CLI not found\|^# HARD GATE" "$result_file" 2>/dev/null; then
        CODEX_PASSED=true
      elif [[ "$codex_status" == "NO_OUTPUT" ]] && grep -q '^# Codex returned NO_OUTPUT' "$result_file" 2>/dev/null \
          && [[ $codex_exit -eq 0 || $codex_exit -eq 5 ]]; then
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
          CODEX_CLI_MISSING=true
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

# --- Iteration cap and preamble injection ---
CURRENT_ITER=0
if [[ -n "$WRK_ID" ]]; then
  CURRENT_ITER="$(get_review_iteration "$WRK_ID")"
  if [[ "$CURRENT_ITER" -ge "$MAX_REVIEW_ITERATIONS" ]]; then
    echo "✖ Review iteration cap reached: ${WRK_ID} has already had ${CURRENT_ITER}/${MAX_REVIEW_ITERATIONS} review passes." >&2
    echo "  No further review passes will be accepted for this WRK." >&2
    echo "  Resolve findings and close the WRK instead of requesting another review." >&2
    exit 1
  fi
  CURRENT_ITER="$(increment_review_iteration "$WRK_ID")"
  ITER_PREAMBLE="You are reviewing ${WRK_ID} — iteration ${CURRENT_ITER} of ${MAX_REVIEW_ITERATIONS} (maximum).

This is a hard budget. After iteration ${MAX_REVIEW_ITERATIONS} no further review passes will be
accepted. Plan your feedback to maximise impact within this constraint:
  * Iteration 1: blockers and security issues only — nothing else
  * Iteration 2: major design / correctness issues
  * Iteration 3: minor / style / nice-to-haves

Front-load your most critical finding first. If you have only one shot to prevent a
serious defect, this is it. Do not save critical issues for a later pass.

---"
  PROMPT="${ITER_PREAMBLE}
${PROMPT}"
fi

# Dispatch
case "$REVIEWER" in
  all)
    submit_review "claude"
    submit_review "codex"
    submit_review "gemini"
    echo "--- All reviews submitted. Results in: ${RESULTS_DIR}/"
    if [[ "$CODEX_PASSED" != "true" ]]; then
      # Codex CLI missing: require explicit user approval to proceed without Codex
      if [[ "$CODEX_CLI_MISSING" == "true" ]]; then
        if [[ "$ALLOW_NO_CODEX" != "true" ]]; then
          echo ""
          echo "=== CODEX HARD GATE BLOCKED: Codex CLI not installed ===" >&2
          echo "Install Codex CLI: npm install -g @openai/codex" >&2
          echo "Or pass --allow-no-codex to proceed with 2-of-3 consensus (requires explicit approval)." >&2
          exit 1
        fi
        echo "    --allow-no-codex: user approved proceeding without Codex; enabling 2-of-3 fallback" >&2
        CODEX_FALLBACK_ALLOWED=true
      fi
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
