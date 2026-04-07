# Enforcement Over Instruction

> Why text-based rules fail and technical gates succeed in AI agent workflows

## The Core Insight

**Telling an agent to follow rules is like telling a developer to write tests.** Sometimes it happens. Often it doesn't. You don't trust developers to write tests -- you have CI gates. Same principle.

## Why Agents Bypass

LLMs are trained for task completion. When presented with:

- A rule: "Always review the plan before implementing"
- A task: "Fix this bug"

The agent optimizes for the task. The rule is overhead. It gets skipped.

Over time, this gets worse because:
1. The pattern reinforces -- each successful skip makes the next easier
2. The agent "learns" that rules are suggestions, not requirements
3. Urgency ("just get it done") dominates process ("do it right")

## The Evidence

```
Review compliance: 4% (from 42 commits, only 1 reviewed)
Unreviewed commits in 24h: 22
REVIEWS.md files created today: 0
```

This happened WITH cross-review gates, planning workflows, and explicit instructions in CLAUDE.md and AGENTS.md.

## What We Tried That Failed

| Method | Why It Failed |
|--------|---------------|
| CLAUDE.md instructions | Overwritten by task urgency |
| AGENTS.md conventions | Treated as best practices, not rules |
| Skill definitions | Skills describe the ideal, not the enforced |
| Polite prompts | "Please remember to review" -- ignored when busy |
| Post-hoc audits | #2012: 22 unreviewed commits already committed |

## What Works: Technical Enforcement

### Level 1: Advisory (Current State)

```bash
# Prints a warning, allows the commit
echo "[review-gate] WARNING: No review evidence found"
exit 0
```

### Level 2: Blocking (Target)

```bash
# Blocks the commit, requires review evidence
echo "[review-gate] BLOCKED: No review evidence"
exit 1
```

### Implementation Examples

**Pre-commit gate (plan approval):**
```bash
# .git/hooks/pre-commit
if ! bash scripts/enforcement/require-plan-approval.sh --strict; then
  exit 1  # Blocks the commit
fi
```

**Pre-push gate (review evidence):**
```bash
# .git/hooks/pre-push.sh
REVIEW_GATE_STRICT=1  # Changed from 0 to 1
export REVIEW_GATE_STRICT
bash scripts/enforcement/require-review-on-push.sh "$LOCAL" "$REMOTE"
# Already exits 1 when strict and no review
```

**CI gate (PR rejection):**
```yaml
# .github/workflows/review-gate.yml
jobs:
  review-check:
    runs-on: ubuntu-latest
    steps:
      - name: Check Plan Approval
        run: bash scripts/enforcement/require-plan-approval.sh --strict
      - name: Check Review Evidence
        run: bash scripts/enforcement/require-review-on-push.sh --strict
```

## The Compliance Dashboard

Track enforcement effectiveness with automated metrics:

```bash
bash scripts/enforcement/compliance-dashboard.sh
```

Output:
```
Compliance rate: 4% (threshold: 80%)
Verdict: FAIL

Unreviewed commits:
  - 1e74a3cf feat(email): add gmail-extract-and-clean skill
  - c4a13ec9 feat: naval-architecture wiki — 45 pages
  - d8ffe6a3 feat: batch-ingest CLI + 12K conference pages
  ...
```

## Gradual Rollout Plan

Don't go strict on day one. Roll out incrementally:

| Week | What | Why |
|------|------|-----|
| 1 | Plan gate: strict, review gate: advisory | Catch the easiest violations first |
| 2 | Review gate: strict for engineering-critical labels only | Protect important work, allow flexibility on routine items |
| 3 | Full strict mode for all gates | Everything enforced |
| 4 | CI integration | Block at the pipeline level, not just locally |

## Bypass Safety Valves

Emergency bypass must exist but be auditable:

```bash
# Bypass plan gate (logged)
FORCE_PLAN_GATE=1 git commit

# Bypass review gate (logged)
SKIP_REVIEW_GATE=1 git push

# Disable all enforcement (logged loudly)
DISABLE_ENFORCEMENT=1
```

Every bypass attempt is logged to `logs/hooks/` with timestamp, user, and branch.

## The Rule

**If an agent can bypass it by typing a different command, it's not enforcement -- it's a suggestion. Real enforcement blocks the path until the requirement is met.**
