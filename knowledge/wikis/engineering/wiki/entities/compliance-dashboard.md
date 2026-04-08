---
title: "Compliance Dashboard"
tags: [system, compliance, monitoring, enforcement]
sources:
  - compliance-dashboard-doc
added: 2026-04-08
last_updated: 2026-04-08
---

# Compliance Dashboard

Automated system that tracks whether AI agents follow the required engineering workflow. Generates compliance reports from commit history.

## Location

`scripts/enforcement/compliance-dashboard.sh`

## Usage

```bash
# Default: last 24h, 80% threshold
bash scripts/enforcement/compliance-dashboard.sh

# Custom: last 72h, 90% threshold
COMPLIANCE_WINDOW_HOURS=72 COMPLIANCE_THRESHOLD=90 \
  bash scripts/enforcement/compliance-dashboard.sh
```

## How It Works

1. Scan recent commits (configurable window)
2. Classify: skip (docs, chore, sync) vs reviewable (feat, fix, refactor)
3. Check each reviewable commit for evidence
4. Calculate rate: reviewed / reviewable * 100
5. Compare to threshold (default 80%)

## Evidence Sources

- Plan approval markers in `.planning/plan-approved/`
- Review files in `.planning/phases/*/REVIEWS.md`
- Review reports in `.claude/reports/*review*`
- Review keywords in commit messages

## Log Files

| File | Location |
|------|----------|
| `compliance-YYYYMMDD.json` | `logs/compliance/` |
| `plan-gate-events.jsonl` | `logs/hooks/` |
| `review-gate-bypass.jsonl` | `logs/hooks/` |

## Cross-References

- **Related concept**: [[compliance-enforcement]]
- **Related concept**: [[enforcement-over-instruction]]
- **Related concept**: [[three-agent-cross-review]]
