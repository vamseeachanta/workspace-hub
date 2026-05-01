# Archived Skill: `adversarial-review-prompt-refresh-guard`

Original path: `/home/vamsee/.hermes/skills/software-development/adversarial-review-prompt-refresh-guard`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/software-development/adversarial-review-prompt-refresh-guard`
Consolidation date: 2026-04-29

---

---
name: adversarial-review-prompt-refresh-guard
description: Prevent stale plan/code review prompts from being sent to Codex/Gemini after the underlying artifact changed.
version: 1.0.0
author: Hermes Agent
category: software-development
tags: [review, adversarial-review, prompt-packaging, codex, gemini, governance]
---

# Adversarial Review Prompt Refresh Guard

Use this when running adversarial plan/code reviews through prompt files such as `.planning/quick/review-<issue>-prompt.md`.

## When to use
- You patched a plan after review findings
- You are running a second/third review wave
- You generate provider prompts from local files before calling `codex exec` / `gemini exec`

## Core risk
A revised plan file can be current while the provider prompt file is stale.
When that happens, reviewers attack already-fixed artifact paths or old deliverables, producing misleading repeat `MAJOR` findings.

## Required workflow
1. After every material plan edit, regenerate the review prompt from the current plan text.
2. Verify the prompt file itself before dispatch.
3. Search the prompt for newly added artifact paths / acceptance criteria.
4. Search the prompt for removed or superseded paths from the earlier draft.
5. Reconcile the plan artifact's own self-referential sections before rerun:
   - `## Adversarial Review Summary`
   - any `Revisions required` / `Revisions made` bullets
   - any open-question text that the latest patch actually resolved
   - any old overall-result line like `FAIL` / `not approval-ready`
6. Only then launch Codex/Gemini.

## Minimal verification pattern
- Regenerate: rewrite `.planning/quick/review-<issue>-prompt.md`
- Verify current content with `read_file()` or `search_files()`
- Confirm:
  - new artifact paths are present
  - removed old paths are absent
  - updated acceptance criteria are present
  - issue body + latest plan text are both included
  - the plan file does not still self-declare stale review state from the previous wave
  - rerun-specific blockers are reflected as either fixed or still-open, not both

### Artifact self-consistency guard
A rerun can fail even with a fresh prompt if the plan file itself still contains stale review narrative.
Common failure mode seen in live use:
- the plan still says `**Overall result:** FAIL`
- `Revisions required` still list changes that are already patched into the draft
- tests/acceptance criteria are updated, but the plan's own review summary still describes the old state

Reviewers treat those contradictions as real defects. Before rerun, update or neutralize stale self-referential sections so the artifact is internally consistent.

## Heuristic
If reviewers complain about paths/artifacts you already fixed, treat stale-prompt packaging as a possible root cause before accepting the finding as a new defect in the current plan.

## Good signs
- prompt file mentions the same paths as the latest plan
- provider output references the new artifact names
- repeated review findings shrink or change after the prompt refresh

## Bad signs
- provider output criticizes deleted artifact paths
- prompt file still contains old report locations
- second-wave review repeats first-wave findings word-for-word despite real plan changes

## Suggested artifact set per issue
- `.planning/quick/review-<issue>-prompt.md`
- `.planning/quick/review-<issue>-codex.out`
- `.planning/quick/review-<issue>-gemini.out`
- `scripts/review/results/YYYY-MM-DD-plan-<issue>-codex.md`
- `scripts/review/results/YYYY-MM-DD-plan-<issue>-gemini.md`

## Why this matters
This guard prevents false negative review cycles, wasted rework, and presenting non-current criticism to the user as if it applied to the latest draft.
