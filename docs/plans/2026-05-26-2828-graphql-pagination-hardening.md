# Plan for #2828: Reconciler fetch hardening — GraphQL pagination (hasNextPage)

> **Status:** draft (needs adversarial review → user approval) · **Complexity:** T2 · **Date:** 2026-05-26
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2828 · **Refs:** #2802 (follow-on from #2820/#2823 review) · **Client:** N/A

## Resource Intelligence Summary
- `scripts/kanban/reconcile.py:fetch_repo_issues()` uses `gh issue list --state all --limit 100000 --json ...`, aborting only when `len(items) >= limit` (hard truncation).
- #2823 added a **count-delta fail-closed guard** (abort when fetched live count < existing card count; `--allow-shrink` override) — the proportionate mitigation for partial-fetch silent deletion, but it depends on the prior board baseline.
- Tests: `tests/test_kanban_reconcile.py` (13) — would extend with a paginated-fetch test double.

## Problem
`gh issue list --limit N` returns an opaque set; a partial-but-nonzero result (paging defect, rate-limit, visibility drift) below the limit looks authoritative. The count-delta guard catches it *relative to the existing baseline* but isn't a structural guarantee (e.g., first run with no baseline, or simultaneous legitimate growth + partial loss).

## Approach
Replace the fetch with **`gh api graphql`** paginating the repository `issues` connection until `pageInfo.hasNextPage == false`, accumulating nodes by cursor. A fetch that cannot exhaust pagination (error mid-loop) **raises** rather than returning a partial set — making partial fetches structurally impossible. Keep the #2823 count-delta guard as defense-in-depth.

## Scope
In: rewrite `fetch_repo_issues` to GraphQL cursor pagination; map fields to the existing card shape; preserve truncation-abort semantics as "incomplete pagination → raise"; tests with a paginated fetcher double (multi-page, mid-page error → raise). Out: changing upsert/board logic; the workflow.

## Risks & mitigations
| Risk | Mitigation |
|---|---|
| GraphQL field mapping diverges from `gh issue list` JSON | golden-test the mapped card shape against the prior fetcher's output for a known repo |
| Rate-limit on many small pages | reasonable page size (e.g., 100); honor `gh api` retry; abort (not partial) on persistent failure |
| Behavior change breaks existing tests | keep the same return type; run the full suite |

## Acceptance criteria
1. `fetch_repo_issues` pages via GraphQL to `hasNextPage=false`; mid-pagination failure raises (no partial return).
2. Tests: multi-page fetch returns the union; a mid-page error → RuntimeError; field-shape parity with the prior fetcher.
3. Full suite green; `reconcile.py --dry-run` unchanged behavior.

## Dependencies
Independent; **do before/with #2826** so the *scheduled* reconciler is robust. Low coupling to Phase 2/3.
