---
name: agent-router-work-queue
description: 'Sub-skill of agent-router: Work Queue (+3).'
version: 2.0.0
category: coordination
type: reference
scripts_exempt: true
---

# Work Queue (+3)

## Work Queue


- Route items during triage: `route.sh --wrk WRK-NNN`
- Tier maps to work queue routes: SIMPLE=A, STANDARD=B, COMPLEX=C

## Cross-Review Pipeline


- Tasks with high `review_quality` dimension trigger multi-agent review
- Integrates with `scripts/review/cross-review.sh`

## Session State


- Respects orchestrator lock from WRK-139 session-state.yaml
- Session pinning prevents agent switches mid-task (30min TTL)

## Audit Trail


- All decisions logged to `scripts/coordination/routing/logs/routing-decisions.jsonl`
- Use `--stats` to query aggregated history
