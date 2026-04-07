#!/usr/bin/env bash
# require-plan-approval.sh — Pre-commit gate: block implementation commits without plan approval
# Level 3 (hard enforcement) — exits 1 to block the commit
# Policy: docs/standards/HARD-STOP-POLICY.md
# Issues: #1876, #2017

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"

# ── Parse arguments ──────────────────────────────────────────────────────
STRICT_MODE="${FORCE_PLAN_GATE_STRICT:-0}"

for arg in "$@"; do
  case "$arg" in
    --strict) STRICT_MODE=1 ;;
    --check) STRICT_MODE=0 ;;  # advisory mode
  esac
done

# ── Detect if this is an engineering commit ──────────────────────────────
get_staged_files() {
  git diff --cached --name-only 2>/dev/null || true
}

needs_plan_approval() {
  local files="$1"
  # Only gate on implementation files (not docs, config, skills)
  if echo "$files" | grep -qE '\.(py|js|ts|sh|rs|go)$'; then
    # But not if only in scripts/, .github/, docs/, config/, .claude/skills/, tests/
    local impl_only
    impl_only="$(echo "$files" | grep -vE '^(scripts/|\.github/|docs/|config/|.claude/skills/|.claude/hooks/|tests/|specs/)' || true)"
    if [[ -n "$impl_only" ]]; then
      return 0  # needs plan approval
    fi
  fi
  # Commit message check — if message starts with feat(/ or fix(, needs approval
  local msg
  msg="$(git diff --cached --format='%s' --no-patch 2>/dev/null || true)"
  if echo "$msg" | grep -qE '^(feat|fix)\('; then
    return 0
  fi
  return 1  # doesn't need approval
}

# ── Check for plan approval evidence ─────────────────────────────────────
has_plan_approval() {
  local repo_root="$1"
  
  # Check 1: .planning/plan-approved/ directory has recent marker
  if find "${repo_root}/.planning/plan-approved/" -name "*.md" -newer "${repo_root}/.planning/STATE.md" 2>/dev/null | grep -q .; then
    return 0
  fi
  
  # Check 2: .planning/phases/*/REVIEWS.md has APPROVE
  if find "${repo_root}/.planning/phases/" -name "REVIEWS.md" -newer "${repo_root}/.planning/STATE.md" 2>/dev/null | xargs grep -ql "APPROVE" 2>/dev/null; then
    return 0
  fi
  
  # Check 3: Recent commit message contains plan review evidence
  if git log --oneline -10 --format='%s' 2>/dev/null | grep -qiE '(plan.*(approved|reviewed)|plan.*(APPROVE|MINOR))'; then
    return 0
  fi
  
  # Check 4: Session log shows plan was reviewed
  if [[ -f "${repo_root}/logs/sessions/latest.jsonl" ]]; then
    if grep -qE '"plan_reviewed"|"plan_approved"' "${repo_root}/logs/sessions/latest.jsonl" 2>/dev/null; then
      return 0
    fi
  fi
  
  return 1
}

# ── Main ─────────────────────────────────────────────────────────────────
main() {
  local files
  files="$(get_staged_files)"
  
  # Low-risk files don't need plan approval
  if ! needs_plan_approval "$files"; then
    echo "[plan-gate] PASS: No implementation changes or low-risk files only."
    exit 0
  fi
  
  # Check for plan approval
  if has_plan_approval "$REPO_ROOT"; then
    echo "[plan-gate] PASS: Plan approval evidence found."
    exit 0
  fi
  
  # No approval found
  local msg="[plan-gate] NO APPROVAL: Implementation changes detected without plan approval."
  
  if [[ "$STRICT_MODE" == "1" ]]; then
    echo "$msg"
    echo ""
    echo "To resolve:"
    echo "  1. Create a plan: /gsd:plan"
    echo "  2. Get it reviewed: /gsd:review --phase 1"
    echo "  3. Approval creates marker in .planning/plan-approved/"
    echo "  4. Then commit and push"
    echo ""
    echo "To bypass (logged): FORCE_PLAN_GATE=1 git commit"
    
    # Log the bypass attempt
    mkdir -p "${REPO_ROOT}/logs/hooks"
    local timestamp
    timestamp="$(date -Iseconds 2>/dev/null || date '+%Y-%m-%dT%H:%M:%S%z')"
    local branch
    branch="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo 'unknown')"
    echo "{\"timestamp\":\"${timestamp}\",\"branch\":\"${branch}\",\"action\":\"plan-gate-blocked\",\"files\":\"$(echo "$files" | head -5 | tr '\n' ',')\"}" >> "${REPO_ROOT}/logs/hooks/plan-gate-events.jsonl"
    
    exit 1
  else
    echo "$msg (advisory mode — commit will proceed)"
    echo "  Plan approval recommended. Set FORCE_PLAN_GATE_STRICT=1 to enforce."
    exit 0
  fi
}

main
