#!/usr/bin/env bash
# require-cross-review.sh — Gate: block PR creation without cross-review evidence
# Enforcement Level 2 (script) per .claude/rules/patterns.md
# Policy: docs/modules/ai/CROSS_REVIEW_POLICY.md
# Issue: #1537

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
STRICT_MODE=false
for arg in "$@"; do
  case "$arg" in
    --strict) STRICT_MODE=true ;;
  esac
done

# --- Detect GSD phase context ---
# Try to find current phase from .planning/STATE.md or recent git activity
find_current_phase_dir() {
  local state_file="${REPO_ROOT}/.planning/STATE.md"
  if [[ -f "$state_file" ]]; then
    # Extract current phase number from STATE.md
    local phase_num
    phase_num=$(grep -oP 'Phase\s+\K[0-9]+(\.[0-9]+)?' "$state_file" | tail -1 || true)
    if [[ -n "$phase_num" ]]; then
      # Find matching phase directory
      local phase_int="${phase_num%%.*}"
      local padded
      padded=$(printf "%02d" "$phase_int")
      local match
      match=$(find "${REPO_ROOT}/.planning/phases/" -maxdepth 1 -name "${padded}-*" -type d 2>/dev/null | head -1)
      if [[ -n "$match" ]]; then
        echo "$match"
        return 0
      fi
    fi
  fi
  return 1
}

# --- Check 1: GSD REVIEWS.md ---
check_gsd_reviews() {
  local phase_dir
  if phase_dir=$(find_current_phase_dir); then
    if [[ -f "${phase_dir}/REVIEWS.md" ]]; then
      echo "PASS: Cross-review found: ${phase_dir}/REVIEWS.md"
      return 0
    fi
  fi
  # Also check all phase dirs for any recent REVIEWS.md
  if find "${REPO_ROOT}/.planning/phases/" -name "REVIEWS.md" -newer "${REPO_ROOT}/.planning/STATE.md" 2>/dev/null | grep -q .; then
    echo "PASS: Recent REVIEWS.md found in phases/"
    return 0
  fi
  return 1
}

# --- Check 2: Quick-mode review artifacts ---
check_quick_reviews() {
  if find "${REPO_ROOT}/.planning/quick/" -name "REVIEWS.md" -mmin -120 2>/dev/null | grep -q .; then
    echo "PASS: Quick-mode REVIEWS.md found (last 2 hours)"
    return 0
  fi
  return 1
}

# --- Check 3: Report-based review evidence ---
check_report_reviews() {
  local today
  today=$(date +%Y-%m-%d)
  if find "${REPO_ROOT}/.claude/reports/" -name "*review*" -newer "${REPO_ROOT}/.planning/STATE.md" 2>/dev/null | grep -q .; then
    echo "PASS: Review report found in .claude/reports/"
    return 0
  fi
  # Check for today's review artifacts
  if find "${REPO_ROOT}/.claude/reports/" -name "${today}*review*" 2>/dev/null | grep -q .; then
    echo "PASS: Today's review report found"
    return 0
  fi
  return 1
}

# --- Check 4: Git evidence of cross-review ---
check_git_review_evidence() {
  # Look for recent commits mentioning review/codex/gemini
  if git log --oneline -20 --format='%s' 2>/dev/null | grep -qiE '(review|codex|gemini|cross-review|adversarial)'; then
    echo "PASS: Recent git commit references cross-review"
    return 0
  fi
  return 1
}

# --- Check 5: Adversarial provider verification ---
# Ensure the review came from a different AI provider, not self-review
check_adversarial_provider() {
  local provider_pattern='codex|gemini|openai'
  local evidence_found=false

  # Scan all REVIEWS.md files in phases/
  while IFS= read -r review_file; do
    if grep -qiE "$provider_pattern" "$review_file" 2>/dev/null; then
      evidence_found=true
      break
    fi
  done < <(find "${REPO_ROOT}/.planning/phases/" -name "REVIEWS.md" 2>/dev/null)

  # Scan quick-mode REVIEWS.md
  if [[ "$evidence_found" == false ]]; then
    while IFS= read -r review_file; do
      if grep -qiE "$provider_pattern" "$review_file" 2>/dev/null; then
        evidence_found=true
        break
      fi
    done < <(find "${REPO_ROOT}/.planning/quick/" -name "REVIEWS.md" 2>/dev/null)
  fi

  # Scan .claude/reports/ review files
  if [[ "$evidence_found" == false ]]; then
    while IFS= read -r report_file; do
      if grep -qiE "$provider_pattern" "$report_file" 2>/dev/null; then
        evidence_found=true
        break
      fi
    done < <(find "${REPO_ROOT}/.claude/reports/" -name "*review*" 2>/dev/null)
  fi

  if [[ "$evidence_found" == true ]]; then
    echo "PASS: Adversarial provider evidence detected in review artifacts"
    return 0
  else
    return 1
  fi
}

# --- Main ---
main() {
  local found=false

  if check_gsd_reviews; then found=true; fi
  if [[ "$found" == false ]] && check_quick_reviews; then found=true; fi
  if [[ "$found" == false ]] && check_report_reviews; then found=true; fi
  if [[ "$found" == false ]] && check_git_review_evidence; then found=true; fi

  if [[ "$found" == false ]]; then
    cat >&2 <<'MSG'
BLOCKED: No cross-review evidence found.

Per CROSS_REVIEW_POLICY.md, PRs require adversarial review before creation.

To unblock, do one of:
  1. Run: /codex:adversarial-review --base main
  2. Run: /gsd:review --phase <N> --codex
  3. For non-GSD work, save review artifacts to .claude/reports/

Policy: docs/modules/ai/CROSS_REVIEW_POLICY.md
Issue: #1537
MSG
    exit 1
  fi

  # Verify the review came from a different provider (adversarial check)
  if ! check_adversarial_provider; then
    if [[ "$STRICT_MODE" == true ]]; then
      cat >&2 <<'MSG'
BLOCKED: Review found but no adversarial provider detected.
In --strict mode, reviews must contain evidence of an external provider (Codex, Gemini, or OpenAI).
Self-review by Claude does not satisfy the cross-review policy.

To unblock, re-run the review using Codex or Gemini:
  /codex:adversarial-review --base main
  /gsd:review --phase <N> --codex

Policy: docs/modules/ai/CROSS_REVIEW_POLICY.md
Issue: #1537
MSG
      exit 1
    else
      echo "WARN: Review found but no adversarial provider detected. Ensure review was done by Codex or Gemini, not self-review."
    fi
  fi

  echo "Cross-review gate: PASSED"
  exit 0
}

main "$@"
