# Archived Skill: `plan-exit-governance-drift-handoff`

Original path: `/home/vamsee/.hermes/skills/coordination/plan-exit-governance-drift-handoff`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/coordination/plan-exit-governance-drift-handoff`
Consolidation date: 2026-04-29

---

---
name: plan-exit-governance-drift-handoff
description: When ending a session on an iterated plan draft, audit and document approval-state drift across GitHub labels, local approval markers, README status, and latest review verdicts.
version: 1.0.0
author: Hermes Agent
category: coordination
tags: [planning, governance, handoff, github, review]
---

# Plan Exit Governance Drift Handoff

Use when:
- A GitHub issue is still in planning/re-review mode
- The plan has gone through multiple adversarial review waves
- You are preparing to exit, hand off, or pause work
- There is any chance older approval state still exists

## Why this matters
A local plan can still be `draft` or "not approval-ready" while the live issue already shows `status:plan-approved` and/or `.planning/plan-approved/<issue>.md` exists from an older state. If you end the session without auditing that, the next operator may incorrectly treat the issue as executable.

## Required exit audit
Before finishing, check all four surfaces:
1. Live GitHub issue state and `status:*` labels
2. Local approval marker `.planning/plan-approved/<issue>.md`
3. `docs/plans/README.md` row status
4. Latest valid provider review verdicts in `scripts/review/results/`

## Required handoff contents
Document explicitly:
- current local plan status (`draft`, `plan-review`, etc.)
- latest valid provider verdicts
- whether the issue is honestly approval-ready or still revision-required
- whether GitHub / local marker / README disagree
- the exact contradiction if drift exists
- that the next session must reconcile approval-vs-review drift before implementation or further advancement

## Recommended wording pattern
- "Live issue shows `status:plan-approved`, but latest valid review evidence still returns MAJOR findings."
- "Local approval marker exists, but current draft remains revision-required."
- "Next session must determine whether approval remains authoritative or whether fresh-review rollback to `status:plan-review` is required."

## Minimal command bundle
```bash
cd /path/to/repo

gh issue view <issue> --json state,labels,title,url
ls -l .planning/plan-approved/<issue>.md
rg -n "\| <issue> \|" docs/plans/README.md
```
Then read the latest provider artifacts for the active plan.

## When to roll back
If fresh review evidence is MAJOR and there is no newer authoritative user approval after the revised draft, the next session should consider the fresh-review rollback routine:
- remove stale `status:plan-approved`
- restore `status:plan-review`
- remove stale local approval marker if appropriate
- sync `docs/plans/README.md`
- leave a governance-cleanup note on the issue

## Output artifacts
Prefer both:
1. a GitHub issue status comment
2. a local exit handoff doc under `docs/handoffs/`

This makes the drift visible both in-repo and on the issue thread.
