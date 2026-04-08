---
name: enforcement-audit-and-upgrade
description: Audit existing enforcement infrastructure, identify gaps between advisory and strict modes, create hard-gate scripts, and incrementally roll out enforcement. Pattern from #1876/#2017 enforcement audit session.
category: coordination
triggers:
  - When asked to audit or improve agent compliance with workflows
  - When review compliance drops below threshold (e.g., 80%)
  - When agents are bypassing established processes
version: 1.0.0
---

# Enforcement Audit and Upgrade Pattern

## Overview

Audit enforcement infrastructure, find the gap between what exists and what actually blocks, then incrementally upgrade from advisory to strict mode.

## Key Finding: Advisory Mode Is No Enforcement

Scripts that print warnings but exit 0 are NOT enforcement. Real enforcement must exit 1 to block the operation. Every existing enforcement mechanism defaults to advisory mode.

## Audit Checklist

1. **Find all enforcement scripts**: `ls scripts/enforcement/`
2. **Find all git hooks**: `ls .git/hooks/ | grep -v sample`
3. **Find all Claude hooks**: `ls .claude/hooks/` + check `.claude/settings.json`
4. **Read each script**: Does it exit 0 (advisory) or exit 1 (blocking)?
5. **Check default mode**: What happens when no env vars are set?
6. **Check hook chain**: Is the enforcement script actually called by the hooks?
7. **Check compliance logs**: `cat logs/hooks/*.jsonl | tail -20`
8. **Run compliance dashboard**: `bash scripts/enforcement/compliance-dashboard.sh`

## Implementation Pattern

### Step 1: Audit existing infrastructure
```bash
# Map what exists
ls scripts/enforcement/
ls .git/hooks/ | grep -v sample
ls .claude/hooks/
cat .claude/settings.json | grep -A5 hooks
```

### Step 2: Identify the gap
Look for:
- Scripts that warn but allow (exit 0 instead of exit 1)
- Hooks that don't call enforcement scripts
- Missing enforcement scripts (e.g., no pre-commit plan gate)
- Compliance metrics far below threshold

### Step 3: Create hard-gate scripts
Three types needed:
1. **require-plan-approval.sh** — pre-commit gate
2. **compliance-dashboard.sh** — metrics and reporting
3. **upgrade-enforcement.sh** — safe transition script

### Step 4: Gradual rollout
Week 1: Plan gate strict, review gate advisory
Week 2: Review gate strict for engineering-critical only
Week 3: Full strict mode
Week 4: CI integration (GitHub Actions)

### Step 5: Document and link
Create methodology docs in `docs/methodology/`:
- compound-engineering.md (the full methodology)
- enforcement-over-instruction.md (why gates beat text)
- Links to all related issues

## Pitfalls

### Compliance metrics are worse than expected
The audit often reveals compliance is much lower than assumed. Document the real numbers (e.g., 4%) — this is the baseline, use it to justify strict mode.

### Bypass mechanisms already exist
Existing scripts support env var bypass (`SKIP_REVIEW_GATE=1`, `GIT_PRE_PUSH_SKIP=1`). Don't remove them — they're safety valves. Log every bypass attempt instead.

### Claude hooks and git hooks are different enforcement levels
Claude PreToolUse hooks only intercept specific tool calls (Write, Edit, Bash). They don't intercept direct git commit/push. Git hooks (.git/hooks/) catch everything. Both are needed.

### Don't go strict on everything at once
Sudden strict mode breaks workflows. Use the upgrade shell script for gradual rollout. Start with the easiest gate to satisfy (plan approval), then escalate.

## Verification

After deployment:
```bash
# Test plan gate blocks without approval
FORCE_PLAN_GATE_STRICT=1 bash scripts/enforcement/require-plan-approval.sh --check

# Test compliance dashboard generates report  
bash scripts/enforcement/compliance-dashboard.sh

# Check logging works
cat logs/hooks/plan-gate-events.jsonl 2>/dev/null || echo "No events yet"
```