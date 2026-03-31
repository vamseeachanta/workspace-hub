#!/usr/bin/env bash
# require-plan-review.sh — Gate: block phase execution without adversarial plan review
# Enforcement Level 2 (script) per .claude/rules/patterns.md
# Policy: docs/modules/ai/CROSS_REVIEW_POLICY.md
# Issue: #1537

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
STRICT_MODE=false
PHASE_NUM=""

for arg in "$@"; do
  case "$arg" in
    --strict) STRICT_MODE=true ;;
    [0-9]*) PHASE_NUM="$arg" ;;
  esac
done

# --- Resolve phase directory from a phase number ---
resolve_phase_dir() {
  local num="$1"
  local phase_int="${num%%.*}"
  local padded
  padded=$(printf "%02d" "$phase_int")
  local match
  match=$(find "${REPO_ROOT}/.planning/phases/" -maxdepth 1 -name "${padded}-*" -type d 2>/dev/null | head -1)
  if [[ -n "$match" ]]; then
    echo "$match"
    return 0
  fi
  return 1
}

# --- Detect current phase from .planning/STATE.md ---
find_current_phase_dir() {
  local state_file="${REPO_ROOT}/.planning/STATE.md"
  if [[ -f "$state_file" ]]; then
    local phase_num
    phase_num=$(grep -oP 'Phase\s+\K[0-9]+(\.[0-9]+)?' "$state_file" | tail -1 || true)
    if [[ -n "$phase_num" ]]; then
      resolve_phase_dir "$phase_num"
      return $?
    fi
  fi
  return 1
}

# --- Get phase directory (from argument or auto-detect) ---
get_phase_dir() {
  if [[ -n "$PHASE_NUM" ]]; then
    if resolve_phase_dir "$PHASE_NUM"; then
      return 0
    fi
    echo "ERROR: No phase directory found matching phase ${PHASE_NUM}" >&2
    exit 1
  fi
  if find_current_phase_dir; then
    return 0
  fi
  echo "ERROR: Cannot detect current phase. Pass a phase number or ensure .planning/STATE.md exists." >&2
  exit 1
}

# --- Check REVIEWS.md for adversarial provider mention ---
# Returns: 0 = adversarial found, 1 = file exists but no provider, 2 = no file
check_adversarial_review() {
  local phase_dir="$1"
  local reviews_file="${phase_dir}/REVIEWS.md"

  if [[ ! -f "$reviews_file" ]]; then
    return 2
  fi

  # Case-insensitive check for adversarial providers
  if grep -qiE '(codex|gemini|openai)' "$reviews_file"; then
    return 0
  fi

  return 1
}

# --- Main ---
main() {
  local phase_dir
  phase_dir=$(get_phase_dir)
  local phase_name
  phase_name=$(basename "$phase_dir")

  echo "Plan-review gate: checking phase ${phase_name}"
  echo "================================================"

  local result
  result=0
  check_adversarial_review "$phase_dir" || result=$?

  case "$result" in
    0)
      echo "PASS: Adversarial plan review found in ${phase_dir}/REVIEWS.md"
      echo ""
      echo "Plan-review gate: PASSED"
      exit 0
      ;;
    1)
      # REVIEWS.md exists but no adversarial provider detected
      if [[ "$STRICT_MODE" == true ]]; then
        cat >&2 <<MSG
BLOCKED (--strict): REVIEWS.md exists at ${phase_dir}/REVIEWS.md
but no adversarial provider (codex, gemini, openai) was detected.

Per CROSS_REVIEW_POLICY.md, one independent adversarial review is required.

To unblock:
  1. Run: /codex:adversarial-review (plan review)
  2. Run: /gsd:review --phase ${PHASE_NUM:-<N>} --codex
  3. Or manually add adversarial review content to ${phase_dir}/REVIEWS.md

Policy: docs/modules/ai/CROSS_REVIEW_POLICY.md
Issue: #1537
MSG
        exit 1
      else
        cat >&2 <<MSG
WARNING: REVIEWS.md exists at ${phase_dir}/REVIEWS.md
but no adversarial provider (codex, gemini, openai) was detected.

Per CROSS_REVIEW_POLICY.md, one independent adversarial review is required.
Consider running: /codex:adversarial-review or /gsd:review --phase ${PHASE_NUM:-<N>} --codex

Use --strict to make this a blocking error.
MSG
        echo ""
        echo "Plan-review gate: PASSED (with warning)"
        exit 0
      fi
      ;;
    2)
      # No REVIEWS.md at all
      cat >&2 <<MSG
BLOCKED: No REVIEWS.md found at ${phase_dir}/REVIEWS.md

Per CROSS_REVIEW_POLICY.md, phase execution requires adversarial plan review.

To unblock, do one of:
  1. Run: /codex:adversarial-review (plan review)
  2. Run: /gsd:review --phase ${PHASE_NUM:-<N>} --codex
  3. Manually create ${phase_dir}/REVIEWS.md with adversarial review content

Policy: docs/modules/ai/CROSS_REVIEW_POLICY.md
Issue: #1537
MSG
      exit 1
      ;;
  esac
}

main "$@"
