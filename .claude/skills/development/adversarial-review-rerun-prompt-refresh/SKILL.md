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

## Why it matters
Stale review prompts can make a plan look blocked when the latest draft may already have resolved the finding. Prompt freshness is part of review correctness.
