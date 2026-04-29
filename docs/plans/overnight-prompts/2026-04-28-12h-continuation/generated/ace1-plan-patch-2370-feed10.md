# Feed10 — bounded plan patch for #2370 after feed9 MINOR review

Machine: ace-linux-1. Provider: Claude. Mode: non-destructive plan-text patch only.

Stop target: 2026-04-29 09:45 CDT. If current local time is at/after stop target, do not start substantive work; write a short BLOCKED_BY_STOP_TIME result instead.

## Context

Feed8 drafted `docs/plans/2026-04-29-issue-2370-closed-issue-promotion-ledger.md`.
Feed9 reviewed it and wrote `scripts/review/results/2026-04-29-plan-2370-claude-feed9.md` with verdict MINOR. The review says the plan may advance after addressing/acknowledging the MINOR findings.

## Hard boundaries

- Do **not** implement code.
- Do **not** create approval markers.
- Do **not** mutate GitHub: no comments, labels, PRs, closes, merges, force pushes, or issue edits.
- Do **not** commit, push, reset, merge, or close anything.
- Keep writes limited to:
  - `docs/plans/2026-04-29-issue-2370-closed-issue-promotion-ledger.md`
  - `docs/plans/overnight-prompts/2026-04-28-12h-continuation/results/ace1-plan-patch-2370-feed10.md`
- Read-only commands are allowed for verifying source lines.

## Task

Patch the #2370 draft plan to consume the feed9 MINOR findings without expanding scope:

1. Finding 1 — add/adjust resource-intelligence acknowledgement for the retrieval-contract bundle (`data/document-index/registry.yaml`, `data/document-index/resource-intelligence-maturity.yaml`, `docs/document-intelligence/`, issue #2205, issue #2096), with a short relevance/non-relevance rationale. Do not overclaim deep review if only inspected briefly.
2. Finding 2 — remove the claim that the 5 already-ingested issue numbers are unknown. Cite `knowledge/wikis/engineering/wiki/sources/closed-engineering-issues.md` and list #1773, #1791, #1768, #1984, #1858.
3. Finding 3 — clarify exactly which `knowledge/wikis/engineering/SOURCE_INVENTORY.md` sections/counts are in scope for update; keep `knowledge/wikis/engineering/wiki/index.md` out of scope unless the plan explicitly justifies otherwise.
4. Finding 4 — make the composite-score formula unambiguous: subtract `overlap_risk * 0.20` or normalize it before summing. The plan must prevent implementer-time sign ambiguity.
5. Finding 5 — add at least two TDD cases for wiki index parsing edge cases (`[Title](path.md)` links and irregular/loose sections or malformed rows).
6. Finding 8 — define the `--already-ingested` CLI input format. Prefer a simple newline-delimited issue-number text file and/or document extraction from the canonical markdown source.
7. Update the adversarial review summary/status in the plan to record feed9 MINOR and feed10 patch state. Keep status as draft / not approved.

## Verification

Before writing the result summary, verify by read/search that:
- The plan no longer says the exact 5 already-ingested issue numbers are not listed/unknown.
- The explicit overlap-risk sign handling appears in pseudocode or acceptance criteria.
- The `--already-ingested` input format is specified.
- The added TDD cases are present.
- The plan still says NOT APPROVED / draft and does not claim user approval.

## Output requirements

Write `docs/plans/overnight-prompts/2026-04-28-12h-continuation/results/ace1-plan-patch-2370-feed10.md` with:
- classification `COMPLETED_WITH_RESULT` or `BLOCKED`,
- files inspected and files modified,
- a finding-by-finding patch checklist,
- verification commands/checks and observed pass/fail,
- next safe action (likely second-provider cross-review; no GitHub mutation).

End after writing the result summary. No GitHub or git mutation.
