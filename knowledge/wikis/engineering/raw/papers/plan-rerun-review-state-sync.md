# Archived Skill: `plan-rerun-review-state-sync`

Original path: `/home/vamsee/.hermes/skills/software-development/plan-rerun-review-state-sync`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/software-development/plan-rerun-review-state-sync`
Consolidation date: 2026-04-29

---

---
name: plan-rerun-review-state-sync
description: Keep iterative plan-review reruns truthful by syncing prompt files, canonical review artifacts, and the plan's own review-summary narrative after each adversarial wave.
version: 1.0.0
category: software-development
tags: [planning, review, adversarial-review, governance, state-sync]
---

# Plan Rerun Review State Sync

Use when a plan goes through multiple adversarial review waves and you are revising the same plan file repeatedly.

## Problem
Repeated plan reruns create three kinds of drift:
1. old prompt files target outdated plan text
2. canonical review artifacts still reflect older verdicts
3. the plan's own `## Adversarial Review Summary` contradicts the latest draft state

This creates false MAJOR findings like:
- the plan still says FAIL even after a patch
- review artifacts cited in the plan no longer match the current draft
- a newer draft is judged using an older provider prompt or older saved artifact text

## Required workflow after every material plan revision

1. Regenerate the provider prompt from the latest on-disk plan.
2. Save raw provider outputs to a new rerun-specific file:
   - `.planning/quick/review-<issue>-rN-<provider>.out`
3. Overwrite the canonical repo artifact for that provider with the newest substantive verdict:
   - `scripts/review/results/YYYY-MM-DD-plan-<issue>-<provider>.md`
4. Update the plan's own `## Adversarial Review Summary` immediately after the wave.
5. Distinguish clearly between:
   - historical review results
   - current draft state
6. If the current draft has been patched after a failing wave but before the next rerun, the plan summary must say `PENDING RE-REVIEW` rather than continuing to self-declare FAIL for the new draft.

## Strong pattern for the summary section

Use this structure:

```md
## Adversarial Review Summary

Historical review results for the immediately previous draft revision are recorded below for traceability.
They are superseded by the latest patch in this draft and should not be read as the verdict for the current unre-reviewed text.

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | MAJOR | ... |
| Codex | MINOR | ... |
| Gemini | APPROVE | ... |

**Current draft state:** PENDING RE-REVIEW
```

After the next full wave lands, replace that with the actual latest-wave verdicts.

## Additional guardrails

- Do not leave already-satisfied work items in the plan as if still pending.
- If a plan cites `docs/plans/README.md` update work, verify whether the row already exists before keeping that item.
- If a contract/rule is meant to be reusable, avoid tying tests to a single dated artifact when the real rule applies to an artifact class.
- When a reviewer complains about stale artifacts or stale branch-state assumptions, treat that as a plan-state-sync failure first, not necessarily a design failure.

## When a plan is not approval-ready

If any provider still returns MAJOR:
- do not post to GitHub
- do not add `status:plan-review`
- patch the plan again
- regenerate prompt again
- rerun review again

## Why this matters
Without this sync discipline, iterative plan hardening wastes time because each rerun attacks stale state instead of the actual current draft.
