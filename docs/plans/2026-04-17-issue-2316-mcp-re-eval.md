# Plan for #2316: cadence(quarterly) MCP server re-evaluation

> **Status:** plan-review
> **Complexity:** T1 (thin variant of shared cadence-cron design)
> **Date:** 2026-04-17
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2316
> **Base design:** `docs/plans/2026-04-17-cadence-cron-infrastructure.md`
> **Companion:** #1804 (MCP eval: token-optimizer, omega-memory, evalview, insaits)

## What this cadence does

Each quarter, re-tests every configured MCP server against its original value
claim (tokens saved, features unlocked) using the current ecosystem state.
MCPs that have lost value are flagged for pruning.

## Data sources

- `config/mcp/` (MCP configs)
- Last quarter's report: `docs/reports/mcp-re-eval-YYYY-Q.md`
- Token usage corpus (via #1720 mining) — currently sampled from
  `.claude/state/session-signals/cost-tracking.jsonl` + archives

## Headline metric

**Count of MCP servers whose net value declined since last quarter.** Thresholds:
- WARN_COUNT = 1 (one regression worth investigating)
- BLOCK_COUNT = 3 (broad MCP ecosystem drift)

## Report shape

```
# mcp-re-eval — 2026-Q2
**Status:** GREEN — all 4 configured MCPs still net-positive.
## Per-MCP scorecard
| MCP | Claim | This Q | Last Q | Decision |
## Recommended prunes
| MCP | Reason | Config path |
## Candidates to add (from #1804 backlog)
| MCP | Purpose |
## Source
```

## Files to Change

| Action | Path |
|---|---|
| Create | `scripts/cron/mcp-re-eval.sh` |
| Create | `tests/cron/test_mcp_re_eval.py` |
| Create | `docs/reports/mcp-re-eval-2026-Q2.md` (first sample) |
| Append | `scripts/cron/crontab-template.sh` (entry `0 9 1 1,4,7,10 *`) |
| Update | `docs/reports/cadence-schedule.md` |

## Tests

| Test | Verifies |
|------|----------|
| test_mcp_re_eval_lists_all_configured | scorecard row per MCP in config/mcp/ |
| test_mcp_re_eval_green_when_all_positive | all MCPs net-positive → GREEN |
| test_mcp_re_eval_yellow_on_one_regression | 1 regression → YELLOW |
| test_mcp_re_eval_red_on_multiple | ≥3 regressions → RED |
| test_mcp_re_eval_handles_first_run | no baseline → scorecard shows "—" for last Q |
| test_mcp_re_eval_suggests_prunes | MCP with declining value → listed in Recommended prunes |

## Acceptance Criteria

- [ ] 6/6 tests pass.
- [ ] First sample report committed reflecting current MCP configs.
- [ ] Cron quarterly entry in template.

## Risks & Open Questions

- **Open:** How to measure "value" per MCP objectively? Current plan: hand-authored scorecard per MCP with a fixed set of measurable criteria (tokens saved, latency added, error rate). First run establishes baseline.
- **Risk:** token-optimizer's 95% claim (#1804) needs a dedicated benchmark — defer to a follow-up bench in that issue; this cron only reports what the per-MCP scorecard says.
