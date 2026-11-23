---
name: plan-review-prompt-refresh-after-plan-edits
description: Refresh reviewer prompt files from the latest on-disk plan before every adversarial re-review. Prevents Codex/Gemini from critiquing stale plan text after local edits.
version: 1.0.0
author: Hermes Agent
category: workspace-hub-learned
tags: [planning, review, prompt-packaging, codex, gemini, github]
related_skills:
  - multi-provider-adversarial-review
  - gh-work-planning
---

# Plan-review prompt refresh after plan edits

Use when:
- a GitHub issue plan is revised after MAJOR/MINOR review findings
- you are about to rerun Codex/Gemini adversarial plan review
- review prompts are stored in `.planning/quick/review-<issue>-prompt.md` or similar files

## Problem

A common failure mode is to patch the canonical plan file under `docs/plans/...`, then rerun Codex/Gemini using an old prompt file that still contains the previous plan text.

Result:
- reviewers repeat already-fixed findings
- you may think the plan is still blocked for the same reasons
- review artifacts become misleading because they are evaluating stale content, not the current draft

## Rule

After ANY material edit to the plan under review, regenerate the reviewer prompt file from the latest on-disk plan before rerunning reviewers.

Do not reuse old prompt files across review rounds unless you have explicitly rebuilt them from the current plan text.

## Required sequence

1. Edit the canonical plan file.
2. Re-read the latest plan file from disk.
3. Rebuild the review prompt file from that latest text.
4. Verify the prompt file actually contains one or two newly added phrases/artifact paths.
5. Only then dispatch Codex/Gemini.

## Verification pattern

Before dispatch, verify the refreshed prompt includes recent edits.
Examples:
- newly added artifact path
- newly added acceptance-criteria line
- newly added section header

Suggested checks:
- `search_files()` on `.planning/quick/review-<issue>-prompt.md` for the new phrase/path
- or `read_file()` the prompt and confirm the new content is present

## Minimal implementation pattern

- source of truth: `docs/plans/YYYY-MM-DD-issue-<NNN>-<slug>.md`
- derived prompt: `.planning/quick/review-<NNN>-prompt.md`
- raw reviewer logs: `.planning/quick/review-<NNN>-{codex,gemini}.out`
- canonical saved reviews: `scripts/review/results/YYYY-MM-DD-plan-<NNN>-{codex,gemini}.md`

Treat the prompt as a generated artifact, not a durable source.

## Smell test

If a reviewer complains about something you already fixed, suspect stale prompt packaging first.

Typical signals:
- reviewer cites a file path that was removed from the latest draft
- reviewer says a deliverable/artifact is missing even though it now exists in the plan
- Codex and Gemini repeat identical old blockers after a substantial rewrite
- a late background review finishes after you already patched the plan, but you treat that output as if it reviewed the newest draft

## Late-review integration rule

When a background Codex/Gemini review finishes after you have already started revising the plan:

1. read the completed review output
2. integrate only the still-relevant findings into the canonical plan
3. regenerate the prompt file from the newly edited plan
4. rerun review for that issue again before trusting the verdict state

Do not assume `review-<issue>-rN.out` corresponds to the newest plan unless you refreshed the prompt after the last edit.

## Single-issue rerun rule

After integrating a late provider finding for one issue, rerun adversarial review for that issue only.
Do not wait to batch unrelated issues together again if the blocker is local to one plan.

This keeps the feedback loop tight and avoids mixing stale/updated review rounds across different issues.

## Avoid self-referential same-cycle artifacts in plan bodies

When hardening `docs/plans/...` before re-review, do not leave plan-body tables that cite same-cycle provider artifact paths such as:

- `scripts/review/results/<date>-plan-<issue>-claude.md`
- `scripts/review/results/<date>-plan-<issue>-codex.md`
- `scripts/review/results/<date>-plan-<issue>-gemini.md`
- wildcard rows like `scripts/review/results/<date>-plan-<issue>-*.md`

Reason: review fanout scripts may truncate or overwrite target provider files before writing new content. A plan that cites the same files currently being regenerated creates false 0-byte or stale-evidence findings.

Use this pattern instead:

1. Cite only prior-cycle disagreement/synthesis artifacts in the plan body.
2. State that current-cycle Claude/Codex/Gemini artifacts must be generated after this revision and verified non-empty before approval.
3. Require the approval request or closeout comment to cite revision-stamped, non-empty review artifacts, not same-cycle placeholders in the plan.
4. Add a quick scan before validation to reject stale self-references and stale test paths.

Example validation snippet:

```bash
python - <<'PY'
from pathlib import Path
bad = False
for p in Path('docs/plans').glob('*.md'):
    for i, line in enumerate(p.read_text().splitlines(), 1):
        if 'Review artifacts | `scripts/review/results/' in line or '> **Review artifacts:** `scripts/review/results/' in line:
            print(f'{p}:{i}: same-cycle review artifact path: {line}')
            bad = True
        if 'tests/governance/' in line:
            print(f'{p}:{i}: stale governance test path: {line}')
            bad = True
raise SystemExit(1 if bad else 0)
PY
```

## Scope note

This is a packaging/instrumentation problem, not necessarily a plan-quality problem.
Fix the prompt refresh path and same-cycle artifact references first, then interpret any remaining findings.
