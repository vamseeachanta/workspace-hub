# Feed18 — Patch #2374 plan after feed17 MINOR review

You are running unattended as one bounded non-destructive continuation lane on ace-linux-1.

## Scope
Patch only the draft plan for issue #2374 based on feed17's completed adversarial review.

Authoritative inputs:
- Plan: `docs/plans/2026-04-27-issue-2374-transient-promotion-candidate-queue.md`
- Review result: `docs/plans/overnight-prompts/2026-04-28-12h-continuation/results/ace1-plan-review-2374-feed17.md`
- Optional conventional review artifact: `scripts/review/results/2026-04-29-plan-2374-claude-feed17.md`
- Sibling plan for compatibility checks: `docs/plans/2026-04-29-issue-2375-wrk-completions-normalize.md`

## Required work
1. Read feed17 and the #2374 plan.
2. Apply the smallest safe plan-only patch that resolves feed17 MINOR findings F1-F3 and low/stale findings where trivial:
   - align or explicitly caveat `DURABLE_CATEGORIES` compatibility with #2375;
   - fix `scripts/operations/` paths for the three cron scripts to `scripts/cron/`;
   - align or explicitly document `route_domain` process-category divergence with #2375;
   - clean stale self-reference/review-artifact-date parentheticals only where obvious.
3. Do **not** broaden implementation scope. Do **not** create approval markers. Do **not** change labels. Do **not** post GitHub comments.
4. Write a concise result report summarizing exact edits and residual status.

## Allowed writes
- `docs/plans/2026-04-27-issue-2374-transient-promotion-candidate-queue.md`
- `docs/plans/overnight-prompts/2026-04-28-12h-continuation/results/ace1-plan-patch-2374-feed18.md`

## Required result format
Write `results/ace1-plan-patch-2374-feed18.md` with:
- Classification: `COMPLETED_WITH_RESULT` or `BLOCKED`
- Files changed
- Feed17 finding disposition table
- Residual reviewer risk, if any

Stop after this patch/report. No implementation, no GitHub mutation, no commit required.
