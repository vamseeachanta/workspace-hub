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
