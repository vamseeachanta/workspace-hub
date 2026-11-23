# Archived Skill: `re-review-local-plan-artifact-grounding`

Original path: `/home/vamsee/.hermes/skills/software-development/re-review-local-plan-artifact-grounding`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/software-development/re-review-local-plan-artifact-grounding`
Consolidation date: 2026-04-29

---

---
name: re-review-local-plan-artifact-grounding
description: Prevent stale adversarial re-reviews by forcing Codex/Gemini to review the exact revised local plan artifact instead of stale GitHub issue text or default-branch content.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [review, adversarial, codex, gemini, planning, grounding]
    related_skills: [multi-provider-adversarial-review, gh-work-planning]
---

# Re-review Local Plan Artifact Grounding

Use this when:
- a GitHub issue plan was revised locally after earlier review findings
- you are rerunning Codex/Gemini adversarial review
- there is any risk the reviewer will re-ground on stale issue text or `main` branch content

## Problem this solves

A real failure mode in plan re-review is that the provider ignores or underweights the latest local plan edits and instead reviews:
- the stale GitHub issue body
- older review artifacts
- the default branch version of the plan

This can produce a false fresh `MAJOR` against problems that were already removed locally.

## Reliable pattern

1. Save the revised local plan first.
2. Do NOT trust a compact summary-only rerun when the earlier review already drifted to stale remote/main content.
3. Build a review prompt that embeds the exact revised sections inline.
4. Tell the reviewer explicitly:
   - review ONLY the exact inline artifact below
   - do NOT substitute remote/default-branch/GitHub issue content
5. Keep the inline artifact focused on the changed approval-critical sections:
   - Deliverable
   - Scope Boundaries
   - Linkage Strategy
   - Downstream Integration Surface
   - Pseudocode
   - Files to Change
   - TDD Test List
   - Acceptance Criteria
6. If helpful, prepend a short list of already-fixed prior blockers so the reviewer evaluates only the real residual risk.
7. Save raw logs and canonical review artifacts separately.
8. If the rerun still cites stale elements already removed locally, treat that first as a packaging failure and rerun before accepting the verdict.

Important lesson from live use:
- A compact prompt that merely summarizes the revised plan can still let Codex re-ground on stale GitHub/main-branch content and return false MAJOR findings.
- Switching to an artifact-inline prompt that embeds the exact revised local sections can flip the same review from false MAJOR to the real residual verdict (for example MINOR).

## Suggested prompt contract

Use wording like:

```text
Review ONLY the exact inline artifact below.
Do not substitute any remote/main-branch version of the plan.
The local plan was revised after the earlier review.
```

Then list the already-addressed prior blockers so the reviewer evaluates the real residual risk instead of re-litigating old scope.

## Good compact rerun structure

- `.planning/quick/review-<issue>-artifact-inline-prompt.md`
- `.planning/quick/review-<issue>-artifact-inline-codex.out`
- `.planning/quick/review-<issue>-artifact-inline-gemini.out`
- `scripts/review/results/YYYY-MM-DD-plan-<issue>-codex.md`
- `scripts/review/results/YYYY-MM-DD-plan-<issue>-gemini.md`

## Decision rule

If the provider returns findings against content that is not present in the inline artifact:
- classify the run as stale-grounding / packaging failure
- do not accept the verdict yet
- rerun with a tighter inline artifact prompt

## Typical signs of stale grounding

- Reviewer complains about package-root exports that were already removed locally
- Reviewer cites helper APIs that are now explicitly out of scope
- Reviewer references older issue text instead of the narrowed v1 plan
- Reviewer claims the plan still uses a generic field that the local artifact replaced

## When this matters most

This matters most after narrowing a plan in response to earlier MAJOR review findings. In those cases, the difference between stale and correctly grounded re-review can be the difference between:
- false `MAJOR`
- real `MINOR` or `APPROVE`

## Minimal workflow

1. revise local plan
2. create artifact-inline prompt
3. run Codex/Gemini
4. inspect whether findings match the inline artifact
5. only then synthesize verdicts into the GitHub issue
