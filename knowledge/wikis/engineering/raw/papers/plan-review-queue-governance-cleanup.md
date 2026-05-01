# Archived Skill: `plan-review-queue-governance-cleanup`

Original path: `/home/vamsee/.hermes/skills/coordination/plan-review-queue-governance-cleanup`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/coordination/plan-review-queue-governance-cleanup`
Consolidation date: 2026-04-29

---

---
name: plan-review-queue-governance-cleanup
description: Clean a stale `status:plan-review` queue by separating missing-plan drift from real review blockers, posting governance comments, removing stale labels, and materializing durable review artifacts for delegated/Hermes reviews.
version: 1.0.0
author: Hermes Agent
category: coordination
tags: [github, planning, governance, queue-cleanup, adversarial-review]
related_skills:
  - coordination/issue-planning-mode
  - software-development/multi-provider-adversarial-review
  - github/github-issues
  - github/github-comment-body-file-safety
---

# Plan-Review Queue Governance Cleanup

Use when a repo has many open GitHub issues labeled `status:plan-review` and you need to determine which are:
- real plan-review items
- mislabeled missing-plan drift
- reviewed but blocked by fresh MAJOR findings
- plausible approval-track items

## Why this exists

A live `status:plan-review` label alone is not trustworthy. In practice, queues drift in two common ways:
1. issues get labeled `status:plan-review` before a canonical `docs/plans/` artifact exists
2. fresh adversarial review returns MAJOR, but the blocker evidence only exists in chat/logs and never becomes a durable repo artifact + GitHub comment

This skill keeps the queue operationally honest.

## Required evidence surfaces

For each issue, audit all of:
1. live GitHub labels/state
2. canonical local plan file under `docs/plans/*issue-<N>-*.md`
3. local review artifacts under `scripts/review/results/*-plan-<N>-*.md`
4. local approval marker `.planning/plan-approved/<N>.md` if relevant

## Classification

### A. Missing-plan drift
Criteria:
- issue still labeled `status:plan-review`
- no canonical `docs/plans/*issue-<N>-*.md`
- usually no plan-review artifacts either

Action sequence:
1. Post a short governance comment explaining the issue is mislabeled as `status:plan-review` without a canonical local plan artifact.
2. Remove the stale `status:plan-review` label.
3. Do not present the issue as pending approval or pending provider review.
4. Re-enter it into the queue only after a real canonical plan is drafted and review artifacts exist.

## B. Real plan file exists, but fresh review is blocking
Criteria:
- canonical plan file exists
- fresh review returns `MAJOR`
- issue is still being treated as approval-track or under-reviewed

Action sequence:
1. Save a durable repo artifact summarizing the fresh review under:
   `scripts/review/results/YYYY-MM-DD-plan-<issue>-<reviewer>.md`
2. Post a concise GitHub issue comment with:
   - verdict
   - top blockers
   - explicit statement: not approval-ready
   - required next step: revise plan, rerun adversarial review
3. Keep the issue out of approval-ready discussion until the plan is revised.

## C. Review-complete / possible approval-track
Criteria:
- canonical plan exists
- durable review artifacts exist
- no fresh unresolved MAJOR blocker in the latest review wave

Action:
- surface separately as the shortlist for user attention
- still verify latest review verdicts before calling anything approval-ready

## Durable-artifact rule for delegated/Hermes reviews

This is the key live-use lesson.

If you use `delegate_task` or Hermes subagents to review a plan:
- the chat/subagent output is **not** itself a canonical review artifact
- you must materialize a durable summary file in `scripts/review/results/`
- you should also post a concise GitHub issue comment in the same pass

Otherwise later queue audits will miss the blocker evidence because it only lived in chat history.

Recommended naming:
- `scripts/review/results/YYYY-MM-DD-plan-<issue>-hermes-parallel.md`
- or another reviewer suffix that truthfully identifies the source

## GitHub comment safety

When posting governance comments or review summaries, use `gh issue comment --body-file ...`.
Do not inline markdown-heavy comments with `--body`.

## Minimal execution pattern

1. Enumerate open `status:plan-review` issues.
2. For each issue, check plan-file existence and review-artifact existence.
3. Split into buckets:
   - missing-plan drift
   - fresh-MAJOR blocked
   - review-complete / shortlist
4. For missing-plan drift:
   - post governance comment
   - remove stale label
5. For fresh-MAJOR blocked:
   - save durable local review artifact
   - post concise blocker summary comment
6. Recompute the queue and only then present the cleaned shortlist to the user.

## Output format to user

Give counts first, then grouped issue lists:
1. removed from queue as drift
2. blocked by MAJOR findings
3. remaining review-complete shortlist

This makes the next action obvious and avoids mixing governance cleanup with approval decisions.
