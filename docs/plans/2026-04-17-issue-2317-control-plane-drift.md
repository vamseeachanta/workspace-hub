# Plan for #2317: cadence(quarterly) control-plane contract drift audit

> **Status:** plan-review
> **Complexity:** T1 (thin variant of shared cadence-cron design)
> **Date:** 2026-04-17
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2317
> **Base design:** `docs/plans/2026-04-17-cadence-cron-infrastructure.md`
> **Companion:** #1525 (reopened — canonical repo control-plane contract)

## What this cadence does

Each quarter, diffs `AGENTS.md`, `CLAUDE.md`, `MEMORY.md`, `GEMINI.md` across
~15 child repos against the canonical contract defined in #1525. Any repo whose
harness files drift from the contract gets a remediation row in the report.

## Data sources

- Canonical contract: `docs/standards/CONTROL_PLANE_CONTRACT.md`
- Per-repo harness files: `{repo}/{AGENTS,CLAUDE,MEMORY,GEMINI}.md`
- Child repos: all dirs under `/mnt/local-analysis/workspace-hub/*/` with `.git/`

## Headline metric

**Count of child repos with any drift.** Thresholds:
- WARN_COUNT = 1
- BLOCK_COUNT = 5

## Report shape

```
# control-plane-drift — 2026-Q2
**Status:** GREEN — 0/15 child repos drift from canonical contract.
## Per-repo drift status
| Repo | AGENTS.md | CLAUDE.md | MEMORY.md | GEMINI.md | Drift summary |
## Remediation plan (per drifted repo)
| Repo | Drift | Suggested fix |
## Source
```

## Files to Change

| Action | Path |
|---|---|
| Create | `scripts/cron/control-plane-drift.sh` |
| Create | `tests/cron/test_control_plane_drift.py` |
| Create | `docs/reports/control-plane-drift-2026-Q2.md` (first sample) |
| Append | `scripts/cron/crontab-template.sh` (entry `0 10 1 1,4,7,10 *`) |
| Update | `docs/reports/cadence-schedule.md` |

## Tests

| Test | Verifies |
|------|----------|
| test_drift_green_when_all_match | every repo matches contract → GREEN |
| test_drift_yellow_on_one_drift | 1 repo drifts → YELLOW |
| test_drift_red_on_many | ≥5 drift → RED |
| test_drift_detects_missing_file | repo missing required harness file → flagged |
| test_drift_detects_extra_sections | repo has extra required section → flagged |
| test_drift_handles_repo_without_any_harness | fresh repo → summary marks "uninitialized" |

## Acceptance Criteria

- [ ] 6/6 tests pass.
- [ ] First sample report committed.
- [ ] Depends on #1525 landing the canonical contract first — if #1525 is still in planning, this cadence reports "waiting on contract baseline".

## Risks & Open Questions

- **Risk:** Depends on #1525 baseline; until that lands, the cadence emits a placeholder report. Acceptable — cadence script still works, just reports "no baseline yet".
- **Open:** Should drift be measured by AST-parse of markdown or by exact-string match? Current plan: section-header diff + line-limit check only. Stricter semantics require MVP data first.
