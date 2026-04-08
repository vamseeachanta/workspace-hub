---
title: "Compliance Dashboard"
tags: [methodology, compliance, enforcement, monitoring, scripts]
sources:
  - docs/methodology/compliance-dashboard.md
added: 2026-04-08
last_updated: 2026-04-08
---

# Compliance Dashboard

Tracks whether AI agents follow the required engineering workflow: plan → review → implement → review → ship.

## The Scripts

| Script | Purpose |
|--------|---------|
| `compliance-dashboard.sh` | Generates compliance reports from commit history |
| `require-plan-approval.sh` | Pre-commit gate: blocks implementation without plan |
| `require-review-on-push.sh` | Pre-push gate: checks review evidence exists |
| `require-cross-review.sh` | PR creation gate: requires review artifacts |
| `require-tdd-pairing.sh` | TDD gate: warns on unpaired test changes |
| `extract-learnings.sh` | Post-commit: detects patterns worth capturing |
| `cross-agent-bridge.sh` | Syncs agent knowledge across systems |

## How Compliance is Calculated

1. **Scan recent commits** (default: last 24 hours)
2. **Classify each commit**: skip (docs/chore/test) or reviewable (feat/fix/refactor)
3. **Check for evidence**: plan approval markers, REVIEWS.md, review keywords in commit messages
4. **Calculate rate**: reviewed / reviewable × 100
5. **Compare to threshold**: default 80%

## Running

```bash
# Default: last 24h, 80% threshold
bash scripts/enforcement/compliance-dashboard.sh

# Custom window
COMPLIANCE_WINDOW_HOURS=72 COMPLIANCE_THRESHOLD=90 \
  bash scripts/enforcement/compliance-dashboard.sh
```

## Cross-References

- [Enforcement Over Instruction](enforcement-over-instruction.md)
- [Compound Engineering](compound-engineering.md)
