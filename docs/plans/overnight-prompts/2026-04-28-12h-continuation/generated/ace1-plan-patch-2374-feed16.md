# ace1-plan-patch-2374-feed16 — bounded plan patch for #2374 stale wiki-candidate paths

You are running unattended as a safe follow-up lane in the 2026-04-28 12h continuation window.

## Mission

Patch only the planning artifact for workspace-hub issue #2374 to resolve the stale wiki-candidate path hazard identified by feed14/feed15 for #2375.

## Context to read first

- `docs/plans/2026-04-27-issue-2374-transient-promotion-candidate-queue.md`
- `docs/plans/2026-04-29-issue-2375-wrk-completions-normalize.md`
- `docs/plans/overnight-prompts/2026-04-28-12h-continuation/results/ace1-plan-review-2375-feed14.md`
- `docs/plans/overnight-prompts/2026-04-28-12h-continuation/results/ace1-plan-patch-2375-feed15.md`

## Allowed work

- Edit exactly one plan file: `docs/plans/2026-04-27-issue-2374-transient-promotion-candidate-queue.md`.
- Write exactly one result file: `docs/plans/overnight-prompts/2026-04-28-12h-continuation/results/ace1-plan-patch-2374-feed16.md`.
- The patch scope is limited to replacing stale `knowledge-base/wiki-candidates.yaml` references with the current sibling-compatible target path `data/document-index/wrk-wiki-candidates.yaml`, or adding a short coordination note if the plan intentionally needs a different file name.
- Keep the plan status as draft / not approved unless it already says otherwise; do not mark approved.
- You may run read-only validation commands to verify exact references and line counts.

## Hard boundaries

- Do NOT implement code.
- Do NOT create approval markers.
- Do NOT add/remove labels, post issue comments, create PRs, merge, close, push, force-push, hard reset, or mutate GitHub.
- Do NOT edit #2375 or other sibling plans.
- Do NOT broaden #2374 scope beyond stale-path correction and a concise residual-risk note.
- Do NOT launch additional agents.

## Result file requirements

Write a concise markdown result with:

1. Classification: `COMPLETED_WITH_RESULT`, `BLOCKED`, or `STALLED_NO_OUTPUT`.
2. Exact stale references found and how each was patched.
3. Files written.
4. Verification commands/read checks performed.
5. Residual risks and next safe action.
6. Boundary compliance statement.
