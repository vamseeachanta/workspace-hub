# Archived Skill: `avoid-empty-review-artifact-evidence-in-plan-redrafts`

Original path: `/home/vamsee/.hermes/skills/workspace-hub-learned/avoid-empty-review-artifact-evidence-in-plan-redrafts`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/workspace-hub-learned/avoid-empty-review-artifact-evidence-in-plan-redrafts`
Consolidation date: 2026-04-29

---

---
name: avoid-empty-review-artifact-evidence-in-plan-redrafts
description: Keep plan redrafts truthful during adversarial rerun loops by never citing zero-byte or not-yet-generated review artifacts as resolved evidence.
version: 1.0.0
tags: [planning, adversarial-review, evidence, github, governance]
---

# Avoid Empty Review Artifact Evidence in Plan Redrafts

Use when redrafting a plan after Codex/Gemini/Claude MAJOR findings and preparing a fresh adversarial rerun.

## Problem
A common failure mode in plan-redraft loops is updating the plan text to say the latest MAJOR findings were "addressed" and citing same-day review artifact paths before the rerun has actually completed. If those artifact files are empty or placeholders at review time, the next reviewer correctly flags the plan as evidence-weak or internally contradictory.

## Rule
Do not claim a fresh review wave is resolved unless the corresponding review artifacts:
1. exist on disk
2. are non-empty
3. actually contain the cited verdict/findings

Zero-byte files, placeholder files, or paths that will only be populated later do not count as evidence.

## Recommended wording
If you have redrafted the plan but have not yet completed the rerun, use wording like:
- "fresh adversarial rerun pending"
- "latest redraft prepared for rerun"
- "prior MAJOR findings addressed in draft; verification pending fresh review"

Avoid wording like:
- "Codex MAJOR addressed"
- "Gemini findings resolved"
- "latest review confirms ..."

unless the new artifact is already present and non-empty.

## Practical workflow
1. Redraft the plan against the last completed review artifacts.
2. In `## Adversarial Review Summary`, keep the historical verdicts truthful.
3. If describing the new draft, explicitly mark rerun status as pending.
4. Run the fresh provider review.
5. Verify the new review files are non-empty.
6. Only then update the summary to say the new review wave produced MINOR/APPROVE/MAJOR and whether the plan is approval-ready.

## Verification pattern
Before citing a review artifact in the plan body or summary, check:
- `wc -c scripts/review/results/<file>.md`
- `read_file()` or `terminal("sed -n '1,40p' ...")`
- `git status -s scripts/review/results/` to catch deleted/renamed tracked stubs or untracked real artifacts
- `git ls-tree -r --name-only HEAD scripts/review/results | grep <issue>` after commit to verify the committed evidence paths match the plan's header / Artifact Map

Minimum acceptable evidence:
- a verdict line
- a summary line
- at least one substantive finding or explicit statement of what was checked
- the exact cited artifact path is non-empty and committed when requesting user approval

## Round-archiving rule for mutable fanout outputs

If the review fanout writes mutable provider paths like `YYYY-MM-DD-plan-<issue>-claude.md`, do not `mv` a valid artifact away and then cite the now-empty/missing mutable path in the plan. Prefer one of these safe patterns:
1. Copy the populated mutable file to an immutable round path (`...-claude-r2.md`) after verifying it is non-empty, then update the plan to cite the immutable path; or
2. Keep citing the mutable path, but do not move it and verify it remains populated after any rerun.

If a rerun fails and leaves `*.md` as 0 bytes with only a `*.err` sidecar, treat that run as provider-infrastructure evidence only. Either rerun successfully or cite an explicit unavailable/waiver artifact; never let the plan's front-matter or Artifact Map point at the 0-byte file.

## Why this matters
This prevents self-inflicted review failures where the plan appears to claim evidence that does not yet exist. It keeps approval-stage artifacts honest and avoids wasting a rerun on governance contradictions instead of real plan quality.
