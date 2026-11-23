# Archived Skill: `adversarial-review-rerun-prompt-refresh`

Original path: `/home/vamsee/.hermes/skills/development/adversarial-review-rerun-prompt-refresh`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/development/adversarial-review-rerun-prompt-refresh`
Consolidation date: 2026-04-29

---

---
name: adversarial-review-rerun-prompt-refresh
description: Prevent stale rerun reviews by regenerating provider prompt files from the latest plan or diff before every adversarial review rerun.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [review, adversarial, prompt-refresh, codex, gemini, planning]
    related_skills: [multi-provider-adversarial-review, gh-work-planning]
---

# Adversarial Review Rerun Prompt Refresh

Use when a plan/code review is being rerun after edits.

## Problem
A common failure mode in multi-provider review loops is rerunning Codex/Gemini against an old prompt file after the plan has already been edited. Reviewers then keep flagging defects that were already fixed, creating fake churn and misleading "still MAJOR" results.

## Rule
After ANY material edit to the plan, diff, or acceptance criteria:
1. Regenerate the review prompt file from the latest artifact text.
2. Verify the prompt file contains the new artifact paths / deliverables / acceptance criteria.
3. Only then dispatch the rerun.

Do not assume `.planning/quick/review-<issue>-prompt.md` is current just because the filename is the same.

## Minimal workflow
1. Read the latest plan/diff from disk.
2. Rewrite the prompt file from scratch.
3. Verify with a quick check:
   - `read_file` on the prompt file, or
   - `grep` for newly added artifact names / changed acceptance-criteria phrases.
4. Launch Codex/Gemini review.
5. Save new outputs to a new raw log filename (`-r2`, `-r3`, etc.) so stale logs are not confused with the latest wave.

## What to verify before rerun
- New artifact paths are present in the prompt
- Removed artifacts are no longer mentioned
- Updated acceptance criteria are reflected
- Updated deliverable wording is reflected
- Reviewer is seeing the latest plan text, not a cached or older draft
- If the plan depends on live GitHub child issues, refresh the child issue bodies before rerun and include their current semantics in the prompt; reviewers may verify the live issue bodies rather than trusting the parent plan.
- If artifacts are local/uncommitted, label them explicitly as local drafts. Do not present local plan/review files as durable `main` artifacts unless they are actually pushed or otherwise fetchable from the reviewer’s vantage point.
- Re-check live prerequisite claims that reviewers can falsify from issue comments or CI state (for example “black/isort are green” vs current lint drift). When a historical CI run passed an earlier gate but current main regressed, state both facts and assign final proof ownership explicitly.

## Additional stale-state checklist for plan reruns

After each review wave, do not only refresh the provider prompt file. Also sync the plan document itself so the next reviewers are not reading contradictory metadata.

Before rerunning, explicitly verify and update all of these when applicable:
- frontmatter/header `Review artifacts:` paths point to the latest review wave you want considered canonical
- `Artifact Map` review-artifact rows use the same timestamp/path set as the header
- `Acceptance Criteria` references to review artifacts or verdict gates use the same latest timestamp/path set
- `Adversarial Review Summary` reflects the latest actual wave verdicts rather than an older MAJOR wave
- any `Wave N overall result` text matches the current state of the document after edits
- stale future-tense text like `will reconcile in the next revision` is removed once that reconciliation is already present
- summary tables like `Path Decision Summary` still match the body after revisions; these often drift and trigger repeated MAJOR findings
- diagnostics vs verification are separated cleanly: preconditions/diagnostics stay in the pseudocode or prereq section, while green-state checks stay in the TDD/verification section

## Common multi-wave rerun failure pattern

When a plan goes through 3+ adversarial waves, providers often keep returning MAJOR not because the technical fix is wrong, but because the plan's own metadata becomes internally inconsistent:
- old review-artifact timestamps remain in one section but not another
- acceptance criteria still reference old wave outputs
- the review summary still says MAJOR after the body has already incorporated the fixes
- decision-summary tables still describe pre-revision logic

This creates fake churn. Fix the plan metadata and decision tables before assuming another technical redesign is needed.

## Signs you hit this bug
- Reviewer repeats a MAJOR finding you already fixed
- Review output mentions file paths no longer present in the plan
- Raw prompt file still contains old artifact names after you edited the plan
- Different reviewers seem to be critiquing different versions of the same draft

## Recommended naming
- Prompt: `.planning/quick/review-<issue>-prompt.md`
- Raw logs: `.planning/quick/review-<issue>-codex-rN.out`, `.planning/quick/review-<issue>-gemini-rN.out`
- Canonical artifacts: `scripts/review/results/YYYY-MM-DD-plan-<issue>-<provider>.md`

## Live issue-body drift during plan review

When iterative reviews move a local plan forward but the original GitHub issue body still contains stale assumptions, reviewers may keep flagging a source-of-truth contradiction even if the plan itself is clean. If the stale body is not worth rewriting wholesale, post an explicit superseding GitHub comment before applying `status:plan-review`.

Pattern proven on #2452:
1. r4 Codex returned MINOR only because the original issue body still said Black/isort were green while the plan disclosed they were now red.
2. The fix was not another plan redesign; it was a superseding plan-review packet comment that explicitly overrode the stale body wording, linked the current plan artifact, and summarized latest reviewer verdicts.
3. Only after that comment was posted was it safe to apply `status:plan-review`.

Reusable rule:
- Before moving a plan to `status:plan-review`, compare the original issue body with the latest plan assumptions.
- If they disagree on scope, gates, child ownership, or current CI state, either edit the issue body or post a clearly worded superseding comment.
- In the plan’s evidence/artifact sections, label local/uncommitted files as local drafts until they are actually pushed/fetchable from the reviewer’s vantage point.

## Why it matters
Stale review prompts can make a plan look blocked when the latest draft may already have resolved the finding. Prompt freshness is part of review correctness, and live issue-body drift can create the same false blocker even when prompts are fresh.
