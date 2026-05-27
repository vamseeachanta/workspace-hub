# Code-stage review — #2827 corrected fix (Claude)

- **Artifacts:** `.claude/memory/kanban/scripts/load.py`, `SCHEMA.yaml`, `README.md`, `scripts/install/setup-kanban-loader-timer.sh`, `tests/memory/test_kanban_load.py`, `tests/setup/test_setup_kanban_loader_timer.sh`
- **Reviewer:** Claude (Opus 4.7); verifies the fix implements Codex's prescribed design (Codex's first review found the bug + specified this fix → r3-inline, no re-dispatch)
- **Date:** 2026-05-27
- **Verdict:** **MINOR** — fix source-verified + hermetic-tested; **live smoke deferred (gateway active)**

## Verification (not trusting the subagent)
- Re-ran both suites: `tests/memory/test_kanban_load.py` **8 passed**; `tests/setup/test_setup_kanban_loader_timer.sh` **23 PASS**. ✓
- Read the corrected loader: `create --initial-status running` (block-ELIGIBLE) → `block <id> <reason>` (running→blocked emits the sticky event). Idempotency: status from `create --json`; `block` only when status ∈ {running, ready}; **skip if already blocked** (avoids the `_cmd_block` comment-bloat + the false-failure on re-run that Codex flagged). Fails loud on no-id / eligible-block failure. ✓
- The fix matches Codex's source-read prescription: `block_task` SQL `... WHERE status IN ('running','ready')` + sticky event only on a 1-row update; the gateway's `_has_sticky_block` keys on that event. Creating `running` first makes the transition (and event) fire. ✓ — this is the mechanism the original create-blocked→block could never satisfy.
- MINORs fixed: `SCHEMA.yaml` triage-is-safe claims corrected; timer `interval_to_cron_schedule()` now validates/rejects non-minute intervals (`90m`/`2h`) instead of emitting bad cron.

## Residual (must be honest)
| # | Item | Disposition |
|---|---|---|
| R1 | **Live smoke deferred** — the Hermes gateway is active (PID 3258679), so creating a live throwaway card to prove the sticky event fires would risk the auto-unblock/spawn hazard. Relied on source-verification (conclusive) + hermetic command-sequence tests + `--dry-run`. | **Pre-close gate:** run the one-shot live smoke (create-running→block on a throwaway board, confirm the `task_events` sticky row, clean up) during a **gateway-idle** window before #2827 is closed. Not a code defect; a verification step that's unsafe to run now. |

## Why this is sufficient to PR (but not yet to close)
The bug was a mock-vs-live divergence (`feedback_mock_vs_live_invocation_divergence`): the old mock asserted a `block` success that fails live. The fix is grounded in the **live source** (the SQL + event logic are unambiguous), and the hermetic tests now assert the *command sequence* the source requires. That's strong enough to land the code; the live execution proof is the remaining pre-close item, deliberately deferred for safety.

## Recommendation
PR the fix with R1 flagged. #2827 stays open until the gateway-idle live smoke confirms the sticky event in practice — then completeness scorecard + close.
