#!/usr/bin/env bash
# upgrade-enforcement.sh — Promote advisory enforcement to strict mode
# Issues: #1876, #2017
# 
# This script upgrades existing infrastructure from advisory (warnings only)
# to strict enforcement (blocking). It does this incrementally:
#
# Phase 1: Enable strict mode for plan gate
# Phase 2: Enable strict mode for review gate  
# Phase 3: Enable strict mode for push gate
#
# Each phase can be independently enabled/disabled.
# SKIP: Set DISABLE_ENFORCEMENT=1 to restore advisory mode.

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"

echo "============================================================"
echo "Enforcement Upgrade — Advisory -> Strict Mode"
echo "============================================================"
echo ""

# ── Check Current State ───────────────────────────────────────────────
echo "Current enforcement infrastructure:"
echo ""

# Check 1: Pre-push hook
if [[ -f ".git/hooks/pre-push.sh" ]]; then
  echo "  [OK]   .git/hooks/pre-push.sh exists ($(wc -l < .git/hooks/pre-push.sh) lines)"
else
  echo "  [MISSING] .git/hooks/pre-push.sh not found"
fi

# Check 2: Review gate
if [[ -f "scripts/enforcement/require-review-on-push.sh" ]]; then
  echo "  [OK]   require-review-on-push.sh exists"
else
  echo "  [MISSING] require-review-on-push.sh not found"
fi

# Check 3: Plan gate
if [[ -f "scripts/enforcement/require-plan-approval.sh" ]]; then
  echo "  [OK]   require-plan-approval.sh exists (NEW)"
else
  echo "  [NEW]  require-plan-approval.sh not yet created"
fi

# Check 4: Compliance dashboard
if [[ -f "scripts/enforcement/compliance-dashboard.sh" ]]; then
  echo "  [OK]   compliance-dashboard.sh exists (NEW)"
else
  echo "  [NEW]  compliance-dashboard.sh not yet created"
fi

# Check 5: Claude hook
if [[ -f ".claude/hooks/cross-review-gate.sh" ]]; then
  echo "  [OK]   Claude cross-review-gate.sh exists ($(wc -l < .claude/hooks/cross-review-gate.sh) lines)"
else
  echo "  [MISSING] Claude cross-review-gate.sh not found"
fi

# Check 6: Settings hook config
if [[ -f ".claude/settings.json" ]]; then
  if grep -q "cross-review-gate" .claude/settings.json 2>/dev/null; then
    echo "  [OK]   Claude settings references cross-review-gate"
  else
    echo "  [WARN]  Claude settings does not reference cross-review-gate"
  fi
fi

echo ""
echo "============================================================"
echo "Current Compliance State"
echo "============================================================"

# Run quick compliance check
bash scripts/enforcement/compliance-dashboard.sh 2>/dev/null || true

echo ""
echo "============================================================"
echo "Upgrade Steps (run individually or all together)"
echo "============================================================"
echo ""
echo "Step 1: Enable plan gate strict mode"
echo "  echo 'FORCE_PLAN_GATE_STRICT=1' >> .claude/.env"
echo "  echo 'export FORCE_PLAN_GATE_STRICT=1' >> .git/hooks/enforcement-env"
echo ""
echo "Step 2: Enable review gate strict mode"  
echo "  echo 'REVIEW_GATE_STRICT=1' >> .claude/.env"
echo ""
echo "Step 3: Add enforcement env to git hook chain"
echo "  Update .git/hooks/pre-push.sh to source enforcement-env"
echo ""
echo "Step 4: Wire plan gate into pre-commit"
echo "  Add enforcement call to .git/hooks/pre-commit"
echo ""
echo "To bypass (temporary):"
echo "  export DISABLE_ENFORCEMENT=1"
echo ""
echo "============================================================"
echo "Ready to upgrade? Run: bash scripts/enforcement/upgrade-enforcement.sh --apply"
echo "============================================================"

# ── Apply Mode ─────────────────────────────────────────────────────────
if [[ "${1:-}" == "--apply" ]]; then
  echo ""
  echo "Applying enforcement upgrades..."
  echo ""
  
  # Step 1: Create enforcement env file
  mkdir -p .claude .git/hooks
  cat > .git/hooks/enforcement-env << 'ENV'
# Enforcement environment — controls strict mode for all gates
# Set to 0 for advisory, 1 for strict blocking
export FORCE_PLAN_GATE_STRICT="${FORCE_PLAN_GATE_STRICT:-0}"
export REVIEW_GATE_STRICT="${REVIEW_GATE_STRICT:-0}"
ENV
  chmod 644 .git/hooks/enforcement-env
  echo "  [1/4] Created enforcement env file"
  
  # Step 2: Wire enforcement env into pre-push hook (if not already there)
  if ! grep -q "enforcement-env" .git/hooks/pre-push.sh 2>/dev/null; then
    # Add sourcing after the shebang block
    sed -i '/^set -euo pipefail/a\\n# Source enforcement environment\nif [[ -f "${SCRIPT_DIR}/enforcement-env" ]]; then\n  source "${SCRIPT_DIR}/enforcement-env"\nfi' .git/hooks/pre-push.sh
    echo "  [2/4] Wired enforcement env into pre-push.sh"
  else
    echo "  [2/4] enforcement-env already wired into pre-push.sh"
  fi
  
  # Step 3: Wire plan gate into pre-commit (if not already there)
  if ! grep -q "require-plan-approval" .git/hooks/pre-commit 2>/dev/null; then
    # Read existing pre-commit
    local existing
    existing="$(cat .git/hooks/pre-commit)"
    
    cat > .git/hooks/pre-commit << 'PRECOMMIT'
#!/usr/bin/env bash
# pre-commit — Plan gate enforcement
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"

# Source enforcement environment
if [[ -f "${REPO_ROOT}/.git/hooks/enforcement-env" ]]; then
  source "${REPO_ROOT}/.git/hooks/enforcement-env"
fi

# Skip if enforcement disabled
if [[ "${DISABLE_ENFORCEMENT:-0}" == "1" ]]; then
  echo "[pre-commit] Enforcement disabled (DISABLE_ENFORCEMENT=1)"
  exit 0
fi

# Run plan approval gate
PLAN_GATE="${REPO_ROOT}/scripts/enforcement/require-plan-approval.sh"
if [[ -f "$PLAN_GATE" ]]; then
  bash "$PLAN_GATE" --check
fi

# --- Original pre-commit logic follows ---
PRECOMMIT
    
    # Append original pre-commit logic (everything after the original shebang)
    tail -n +2 "$REPO_ROOT/.git/hooks/pre-commit.bak" >> .git/hooks/pre-commit 2>/dev/null || true
    
    chmod +x .git/hooks/pre-commit
    echo "  [3/4] Wired plan gate into pre-commit"
  else
    echo "  [3/4] plan gate already wired into pre-commit"
  fi
  
  # Step 4: Set strict mode as default (gradual rollout)
  # Start with plan gate strict, review gate advisory, then escalate
  sed -i 's/FORCE_PLAN_GATE_STRICT="${FORCE_PLAN_GATE_STRICT:-0}"/FORCE_PLAN_GATE_STRICT="${FORCE_PLAN_GATE_STRICT:-1}"/' .git/hooks/enforcement-env
  echo "  [4/4] Set FORCE_PLAN_GATE_STRICT=1 (advisory: REVIEW_GATE_STRICT still at 0)"
  
  echo ""
  echo "============================================================" 
  echo "Enforcement enabled!"
  echo ""
  echo "  Plan gate: STRICT (will block commits without plan approval)"
  echo "  Review gate: ADVISORY (warns but doesn't block)"
  echo "  Push gate: existing checks continue"
  echo ""
  echo "To change strictness:"
  echo "  Edit .git/hooks/enforcement-env"
  echo "============================================================"
fi
