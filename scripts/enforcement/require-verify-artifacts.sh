#!/usr/bin/env bash
# require-verify-artifacts.sh — Gate: verify step must include cross-review of code, TDD, artifacts
# Enforcement Level 2 (script) per .claude/rules/patterns.md
# Policy: docs/modules/ai/CROSS_REVIEW_POLICY.md
# Issue: #1537

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"

failures=()
warnings=()

# --- Detect changed files since branch divergence ---
get_changed_files() {
  local base
  base=$(git merge-base HEAD main 2>/dev/null || echo "HEAD~10")
  git diff --name-only "$base"..HEAD 2>/dev/null || true
}

# --- Check 1: Cross-review evidence (code review) ---
check_code_review() {
  local found=false

  # GSD REVIEWS.md
  if find "${REPO_ROOT}/.planning/phases/" -name "REVIEWS.md" -newer "${REPO_ROOT}/.planning/STATE.md" 2>/dev/null | grep -q .; then
    found=true
  fi
  # Quick-mode reviews
  if [[ "$found" == false ]] && find "${REPO_ROOT}/.planning/quick/" -name "REVIEWS.md" -mmin -120 2>/dev/null | grep -q .; then
    found=true
  fi
  # Report-based reviews
  if [[ "$found" == false ]] && find "${REPO_ROOT}/.claude/reports/" -name "*review*" -mmin -120 2>/dev/null | grep -q .; then
    found=true
  fi

  if [[ "$found" == false ]]; then
    failures+=("CODE_REVIEW: No cross-review artifact found. Run /gsd:review --codex or save review to .claude/reports/")
  else
    echo "  PASS: Code cross-review evidence found"
  fi
}

# --- Check 2: TDD evidence (tests alongside implementation) ---
check_tdd_evidence() {
  local changed_files
  changed_files=$(get_changed_files)

  if [[ -z "$changed_files" ]]; then
    warnings+=("TDD: No changed files detected — cannot verify test coverage")
    return
  fi

  # Check if implementation files have corresponding test files
  local has_impl=false
  local has_tests=false

  while IFS= read -r f; do
    # Skip non-code files
    case "$f" in
      *.md|*.json|*.yaml|*.yml|*.txt|*.csv|*.toml|*.cfg|*.ini|*.lock) continue ;;
    esac
    # Skip test files themselves, docs, and config
    case "$f" in
      tests/*|test/*|*_test.*|*test_*|*.test.*|*spec.*) has_tests=true; continue ;;
      docs/*|.claude/*|.planning/*|.codex/*|.gemini/*) continue ;;
    esac
    has_impl=true
  done <<< "$changed_files"

  if [[ "$has_impl" == true && "$has_tests" == false ]]; then
    failures+=("TDD: Implementation files changed but no test files modified. Add tests for changed code.")
  elif [[ "$has_impl" == true && "$has_tests" == true ]]; then
    echo "  PASS: TDD evidence — both implementation and test files changed"
  elif [[ "$has_impl" == false ]]; then
    echo "  PASS: No implementation code changed (docs/config only) — TDD not required"
  fi
}

# --- Check 3: Artifact review (non-code artifacts reviewed) ---
check_artifact_review() {
  local changed_files
  changed_files=$(get_changed_files)

  local has_artifacts=false
  while IFS= read -r f; do
    case "$f" in
      docs/*|scripts/*|*.yaml|*.yml|*.json|*.toml) has_artifacts=true; break ;;
    esac
  done <<< "$changed_files"

  if [[ "$has_artifacts" == true ]]; then
    # Check if REVIEWS.md or review report mentions artifacts/docs/scripts
    local review_covers_artifacts=false
    if find "${REPO_ROOT}/.planning/phases/" -name "REVIEWS.md" -newer "${REPO_ROOT}/.planning/STATE.md" 2>/dev/null -exec grep -qliE '(artifact|doc|script|config|yaml)' {} + 2>/dev/null; then
      review_covers_artifacts=true
    fi
    if [[ "$review_covers_artifacts" == false ]] && find "${REPO_ROOT}/.claude/reports/" -name "*review*" -mmin -120 2>/dev/null -exec grep -qliE '(artifact|doc|script|config|yaml)' {} + 2>/dev/null; then
      review_covers_artifacts=true
    fi

    if [[ "$review_covers_artifacts" == false ]]; then
      warnings+=("ARTIFACTS: Non-code artifacts changed (docs/scripts/config) — ensure review covers them")
    else
      echo "  PASS: Artifact review evidence found"
    fi
  else
    echo "  PASS: No non-code artifacts changed — artifact review not required"
  fi
}

# --- Main ---
main() {
  echo "Verify-step enforcement check (#1537)"
  echo "======================================"

  check_code_review
  check_tdd_evidence
  check_artifact_review

  echo ""

  if [[ ${#warnings[@]} -gt 0 ]]; then
    echo "WARNINGS:"
    for w in "${warnings[@]}"; do
      echo "  - $w"
    done
    echo ""
  fi

  if [[ ${#failures[@]} -gt 0 ]]; then
    echo "BLOCKED: Verify-step checks failed:" >&2
    for f in "${failures[@]}"; do
      echo "  - $f" >&2
    done
    cat >&2 <<'MSG'

Per CROSS_REVIEW_POLICY.md, verification requires:
  1. Cross-review of implementation code
  2. TDD evidence (tests for implementation changes)
  3. Artifact review (docs, scripts, configs)

Policy: docs/modules/ai/CROSS_REVIEW_POLICY.md
Issue: #1537
MSG
    exit 1
  fi

  echo "Verify-step gate: ALL PASSED"
  exit 0
}

main "$@"
