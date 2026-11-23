# Archived Skill: `plan-review-approval-shortlist-audit`

Original path: `/home/vamsee/.hermes/skills/coordination/plan-review-approval-shortlist-audit`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/coordination/plan-review-approval-shortlist-audit`
Consolidation date: 2026-04-29

---

---
name: plan-review-approval-shortlist-audit
description: Audit a status:plan-review queue to identify true approval candidates without being fooled by stale labels, conditional review summaries, or unresolved prerequisite blockers.
version: 1.0.0
author: Hermes Agent
category: coordination
tags: [github, planning, queue-triage, approval-readiness, governance]
---

# Plan-Review Approval Shortlist Audit

Use when the user asks which `status:plan-review` issues are actually ready, closest to ready, or should be surfaced for approval next.

## Why this exists

A naive queue sweep will misclassify issues if it relies only on:
- the presence of a `status:plan-review` label
- the newest review artifact filename
- a single overnight `MINOR` or `approval-ready (conditional)` summary

In practice, the real blocker state often lives across several surfaces at once.

## Required audit surfaces

For each candidate issue, check all of these:

1. Live GitHub issue state
- current `status:*` labels
- issue still open
- recent comments for rollback notes, blocker updates, or recommendation caveats

2. Canonical local plan state
- `docs/plans/YYYY-MM-DD-issue-NNN-*.md`
- `docs/plans/README.md` row status

3. Review evidence
- latest canonical artifact under `scripts/review/results/*-plan-NNN-*.md`
- whether the artifact is real provider review vs placeholder/fallback
- whether a newer GitHub comment sharpens or contradicts the artifact conclusion

4. Approval evidence
- `.planning/plan-approved/NNN.md`
- absence of this marker means the item is still only a recommendation candidate, not approved
- First verify that the checkout used for marker inspection is not stale or behind the target branch. If the active worktree is behind `origin/main`, either fast-forward/use a fresh worktree or inspect the committed remote tree directly (for example `git ls-tree -r --name-only origin/main -- .planning/plan-approved/NNN.md`) before reporting the marker as missing. Stale governance worktrees can otherwise misclassify truly committed approval markers.

5. Explicit prerequisites
- machine constraints (`machine:*` labels)
- blocked-on-other-issue or blocked-on-artifact conditions
- prerequisites documented in comments or review artifacts (e.g. unreadable source PDFs, missing summaries, provider rerun still required)

## Classification buckets

### A. Clean approval candidate
Use only when:
- canonical plan exists
- review coverage is present and recent
- no fresher comment says `needs-revision` / `not ready for user approval`
- no unresolved prerequisite blocker is still active
- issue is still in `status:plan-review`
- no local approval marker yet

### B. Best available approval candidate with caveat
Use when:
- item is stronger than the rest of the queue
- latest review is `MINOR` or `approval-ready (conditional)`
- but a residual condition still exists (for example specific machine requirement)

State the caveat explicitly. Do not silently upgrade to “cleanly approval-ready.”

### C. Needs revision
Use when:
- latest or recent review/comments still record `MAJOR`, `needs-revision`, or unresolved review findings
- approval-readiness depends on provider reruns that have not happened yet
- plan quality may be high, but the review/governance standard has not yet been met

### D. Governance drift / not actually in plan review
Use when:
- live `status:plan-review` exists but there is no canonical plan file
- or there are no review artifacts yet
- or the queue state implies a maturity level the artifacts do not support

## Decision rules

- `MINOR` or `approval-ready (conditional)` is not enough by itself.
- Recent issue comments can overrule simplistic artifact parsing if they document fresher blocker state.
- A best-in-queue recommendation is not the same as certifying all blockers are gone.
- Never describe an item as already approved unless both live state and local approval evidence support that claim.
- Do not mechanically reject a plan just because older per-provider artifacts include `MAJOR`. If a later disagreement/synthesis artifact explicitly says the MAJOR findings were accepted, the plan was revised, residual risk is acceptable, and `Ready for approval: yes`, then treat the synthesis plus latest GitHub comment and README row as the authority. State that the older MAJORs were resolved, not ignored.
- Conversely, if live `status:plan-review` exists but there are no matching review artifacts, or the plan is missing from `docs/plans/README.md`, classify as governance drift/missing-review evidence even if the issue has a plan-draft comment.

## Output format

For a shortlist, return:

1. Approve now
- issue number + title
- why it is the strongest candidate
- residual caveat, if any

2. Keep in revision lane
- issue number + title
- 3-6 bullet punch-list of remaining blockers

3. Optional queue note
- whether the queue still contains governance drift items that should be cleaned before more approval triage

## Practical pattern

If you need a fast but trustworthy pass:
1. enumerate live `status:plan-review` issues
2. separate missing-plan / missing-review drift first
3. inspect latest review artifacts for the remaining set
4. inspect recent GitHub comments for contradiction or conditionality
5. verify no local approval marker exists
6. produce a small shortlist with caveats instead of overclaiming certainty
