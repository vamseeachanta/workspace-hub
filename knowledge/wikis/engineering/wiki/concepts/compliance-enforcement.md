---
title: "Compliance Enforcement"
tags: [compliance, enforcement, scripts, hooks, gates]
sources:
  - compliance-enforcement-doc
added: 2026-04-08
last_updated: 2026-04-08
---

# Compliance Enforcement

The technical infrastructure that ensures AI agents follow the required engineering workflow: plan -> review -> implement -> review -> ship.

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

All scripts live under `scripts/enforcement/` and `scripts/learnings/`.

## Compliance Calculation

1. Scan recent commits (default: last 24 hours)
2. Classify: skip (docs, chore, sync) vs reviewable (feat, fix, refactor)
3. Check reviewable commits for evidence (plan approvals, review files, keywords)
4. Calculate rate: reviewed / reviewable * 100
5. Compare to threshold (default 80%)

## Enforcement Levels

- **Level 1 (advisory)**: prints warnings, allows commit
- **Level 2 (blocking)**: blocks the commit, requires evidence
- **Level 3 (strict)**: `REVIEW_GATE_STRICT=1`, no bypasses

## Cross-References

- **Related concept**: [[enforcement-over-instruction]]
- **Related entity**: [Compliance Dashboard](../entities/compliance-dashboard.md)
- **Related concept**: [[three-agent-cross-review]]
