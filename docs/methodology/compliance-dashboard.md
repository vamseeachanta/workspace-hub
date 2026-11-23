# Compliance Dashboard Guide

> How monitoring, tracking, and enforcement actually works

## What It Is

The compliance dashboard tracks whether AI agents (Claude, Codex, Gemini, Hermes) follow the required engineering workflow: plan -> review -> implement -> review -> ship.

## The Scripts

| Script | Location | Purpose |
|---|---|---|
| `compliance-dashboard.sh` | scripts/enforcement/ | Generates compliance reports from commit history |
| `require-plan-approval.sh` | scripts/enforcement/ | Pre-commit gate: blocks implementation without plan |
| `require-review-on-push.sh` | scripts/enforcement/ | Pre-push gate: checks review evidence exists |
| `require-cross-review.sh` | scripts/enforcement/ | PR creation gate: requires review artifacts |
| `require-tdd-pairing.sh` | scripts/enforcement/ | TDD gate: warns on unpaired test changes |
| `extract-learnings.sh` | scripts/learnings/ | Post-commit: detects patterns worth capturing |
| `cross-agent-bridge.sh` | scripts/learnings/ | Syncs agent knowledge across systems |

## How Compliance is Calculated

1. **Scan recent commits** (default: last 24 hours, configurable)
2. **Classify each commit**:
   - Skip: docs, chore, test, ci, style, sync, merge, revert, build, skill-only, email-only
   - Reviewable: feat, fix, refactor, perf, security
3. **Check each reviewable commit for evidence**:
   - Plan approval markers in `.planning/plan-approved/`
   - Review files in `.planning/phases/*/REVIEWS.md`
   - Review reports in `.claude/reports/*review*`
   - Review keywords in commit messages
4. **Calculate rate**: reviewed / reviewable * 100
5. **Compare to threshold**: default 80%

## Running the Dashboard

```bash
# Default: last 24h, 80% threshold
bash scripts/enforcement/compliance-dashboard.sh

# Custom window: last 72h, 90% threshold
COMPLIANCE_WINDOW_HOURS=72 COMPLIANCE_THRESHOLD=90 \
  bash scripts/enforcement/compliance-dashboard.sh
```

### Example Output

```
============================================================
Compliance Report — Last 24h
============================================================

Total commits:      42
Skipped (docs/etc): 19
Reviewable:         23

Reviewed:           1
Unreviewed:         22
--------------------------------------------
Compliance rate:    4% (threshold: 80%)
Verdict:            FAIL
```

## Log Files

| File | Location | What it tracks |
|---|---|---|
| `compliance-YYYYMMDD.json` | logs/compliance/ | Daily compliance metrics |
| `plan-gate-events.jsonl` | logs/hooks/ | Plan gate blocks/events |
| `review-gate-bypass.jsonl` | logs/hooks/ | Bypass attempts with user/branch |
| `review-gate-latency.jsonl` | logs/hooks/ | Gate execution latency |
| `patterns.jsonl` | logs/learnings/ | Repeated patterns detected |

## Enforcement Levels

```
Level 1 (advisory): Prints warnings, allows commit
  export FORCE_PLAN_GATE_STRICT=0
  export REVIEW_GATE_STRICT=0

Level 3 (hard): Blocks commit, requires fix
  export FORCE_PLAN_GATE_STRICT=1
  REVIEW_GATE_STRICT=1
```

## Integration with GitHub Issues

The compliance dashboard feeds into:

- **#1876** -- Workflow enforcement (implementation)
- **#2012** -- Review backlog audit (daily report)
- **#2017** -- Agent bypass resistance (metrics)

A cron job runs the dashboard and auto-creates issues when compliance drops below threshold.

## Related

- docs/methodology/enforcement-over-instruction.md (why this exists)
- docs/methodology/compound-engineering.md (Lesson 1: enforcement)
- #1876 -- Enforce engineering workflow
- #2017 -- Agent bypass resistance
- #2012 -- Review backlog (4% compliance audit)
