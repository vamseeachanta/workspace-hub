# Code-stage adversarial review — #2847 Phase 1b (wire self-fence into lease path)

> **Stage:** code/artifact · **Issue:** [#2847](https://github.com/vamseeachanta/workspace-hub/issues/2847) · **Date:** 2026-05-29 · **Complexity:** T3 slice
> **Branch:** feat/2847-leader-fence-phase1b

## Method
Independent fresh-context subagent (cross-provider unavailable from a Claude-Code session; degraded T3→1 — a Codex pass on the live-lease-path change is still recommended). Findings main-verified.

## Verdict: CHANGES REQUIRED → resolved

| # | Sev | Finding | Resolution |
|---|-----|---------|------------|
| 1 | MEDIUM | dry-run was fenced, losing the plan-preview (fence is about *origination*; dry-run writes nothing) | gate now `enforce_leader_fence and not dry_run`; test `test_loop_dry_run_is_not_fenced` |
| 2 | MEDIUM | enabling the flag before the ref is bootstrapped halts origination *silently* | gate captures the fence reason into `summary["self_fenced_detail"]` (distinguishes not-leader / store-unavailable / push-unconfirmed); test `..._when_store_unavailable`; enable-runbook note added |
| 3 | LOW | `skipped_due_to_machine` not populated on the fenced early-return | left (diagnostic-only; `self_fenced_detail` explains the empty summary) |
| 4 | LOW | double-read (leader_can_originate.read + may_write_leases.read) | reviewer **confirmed safe** — the 2nd read is authoritative and the CAS binds to it; no change |
| 5 | LOW | lazy-import keyed on bare `dispatch_leader` in sys.modules | left (unique sibling name; production builds the store off the returned module — mismatch surfaces fast) |
| 6 | MEDIUM | test gaps: dry-run-under-fence, loop-level StoreUnavailable, env parsing | all 3 added; env parse extracted to testable `leader_fence_enabled_from_env()` |
| 7 | LOW | per-tick forced push when enabled | documented: a `tick` is one dispatch *invocation* (cron cadence), not a hot loop, so it aligns with the heartbeat design |

## Verification
TDD. **41 passed** (24 dispatch_leader + 17 dispatch-loop; existing 11 dispatch-loop unchanged — default-off path proven identical). Module parses; `bash`/YAML N/A (Python only).

## Default-off safety
`enforce_leader_fence` defaults False; with it off the gate is fully skipped (no store built, no import, no new exception, behavior identical) — `test_loop_default_off_originates_without_a_store`. Enabled only via explicit `DISPATCH_ENFORCE_LEADER_FENCE=1` after the dedicated ref is bootstrapped by the `--heartbeat` watcher.

## Verdict
**APPROVE** after fixes. The fence genuinely blocks origination (tested: `execution_ready==[]` + empty ledger), dry-run preview preserved, halt-reason surfaced. Recommend a Codex pass before flipping the env flag on in production.
