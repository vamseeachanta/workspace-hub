# Feed20 — bounded #2374 plan micro-patch

Run unattended on ace-linux-1 before the 2026-04-29 09:45 CDT launch stop. This is a non-destructive planning-only follow-up to `results/ace1-plan-rereview-2374-feed19.md`.

## Scope

Apply only the three LOW/INFO optional plan edits identified by Feed19 to:

- `docs/plans/2026-04-27-issue-2374-transient-promotion-candidate-queue.md`

Do not edit implementation code, tests, approval markers, GitHub labels/comments/PRs, or other lanes' result files.

## Required edits

1. **Dedup key alignment (Feed19 N2):** Change the TDD test row currently named `test_orchestrator_dedupes_by_source_path_plus_summary` to `test_orchestrator_dedupes_by_normalized_summary_plus_issue_ref`, and make its fixture/expected-result text match the `(normalized summary[:120], issue_ref)` cross-source dedup key described in the Risks section.

2. **Wiki lookup default (Feed19 N3):** Replace the pseudocode assignment that calls `existing_wiki_page_for(c)` with a v1 default-create assignment and an inline comment that wiki-index lookup is deferred to Open Questions.

3. **Score threshold caveat (Feed19 N6):** Add one sentence near the existing line-35 shape-compatibility caveat explaining that #2374 keeps score `>= 1` because Markdown sources are noisier, while #2375 keeps score `>= 2`; unified views must normalize or use a common threshold.

## Verification

After editing, run read-only checks only:

- `grep -n "dedupes_by\|existing_wiki_page_for\|Score threshold\|score >=\|score ≥" docs/plans/2026-04-27-issue-2374-transient-promotion-candidate-queue.md`
- `git diff -- docs/plans/2026-04-27-issue-2374-transient-promotion-candidate-queue.md`

## Result artifact

Write a concise result to:

- `docs/plans/overnight-prompts/2026-04-28-12h-continuation/results/ace1-plan-micropatch-2374-feed20.md`

Include:

- classification (`COMPLETED_WITH_RESULT`, `BLOCKED`, etc.)
- exact files touched
- verification snippets
- next safe follow-up, if any

## Guardrails

- No implementation.
- No tests beyond the read-only grep/diff checks above.
- No commits or pushes.
- No GitHub mutations.
- No approval markers or `status:plan-approved` actions.
- If any required line is not found cleanly, stop and write a blocker result rather than broad-editing.
