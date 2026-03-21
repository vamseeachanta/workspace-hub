# WRK-1389 Plan: Verify dispatch-run.sh — Discrepancy Analysis & Fix Plan

## Scripts-over-LLM Audit
No new scripts needed. All fixes are to existing scripts/templates. Discrepancy fixes will recur for future WRKs but are config/template changes, not new tooling.

## Acceptance Criteria

1. All 9 discrepancies from WRK-5104 (#1252) and WRK-5107 (#1255) categorized with fix/no-fix disposition
2. Fix items captured as new WRKs or appended to existing WRKs
3. GitHub issue #1245 updated with final disposition table

## Discrepancy Disposition Table

| # | Source | Discrepancy | Theme | Disposition |
|---|--------|-------------|-------|-------------|
| D1 | WRK-5104 | Author identity confusion (vamsee vs vamseeachanta vs agent) | Identity | New WRK — standardize author names in stage comments |
| D2 | WRK-5104 | ACs not all checked off at close | Body staleness | Fix in `update-github-issue.py` — sync AC checkboxes from checklist evidence |
| D3 | WRK-5104 | TDD section empty, should show "None" | Body staleness | Fix in `update-github-issue.py` — default empty sections to "None" |
| D4 | WRK-5104 | Future work section says "see evidence file" | Body staleness | Fix in `update-github-issue.py` — inline future-work.yaml summary |
| D5 | WRK-5107 | Stage 17 not treated as human gate | Stage logic | Already fixed — wait-for-approval.sh now wired to stage 17 |
| D6 | WRK-5107 | Stages regurgitated in wrong order | Ordering | Fix in `exit_stage.py` — stage comment numbering from YAML, not LLM |
| D7 | WRK-5107 | Main body not updated in real-time | Body staleness | Fix in stage runners — call update-github-issue.py at stage entry too |
| D8 | WRK-5107 | Too many error codes / red text | Overhead | Related to WRK-1161 — reduce stderr noise in stage scripts |
| D9 | WRK-5107 | Stage overhead exceeds work time | Overhead | Audit stage runner timing; identify bottlenecks for simplification |

## Test Plan

| What | Type | Expected |
|------|------|----------|
| Disposition table covers all 9 discrepancies | Happy | All 9 have fix/no-fix decision |
| Each "fix" item has a WRK reference | Happy | WRK ID or "append to existing" for each |
| No discrepancy left unaddressed | Edge | Zero items with blank disposition |

## Pseudocode
N/A — this is a categorization/triage WRK, not implementation. Fixes will be executed via spawned WRKs.
