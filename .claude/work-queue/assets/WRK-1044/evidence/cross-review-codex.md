# Cross-Review — Codex (Plan Stage 6)

## Verdict: REVISE

## P1 Findings (blocking)

**P1-01**: D2 not a deterministic hard gate — `gate_check.py` PreToolUse only blocks Claude Write tool calls. Shell writes bypass entirely. Must also guard real execution entrypoints (`cross-review.sh`, `claim-item.sh`, `close-item.sh`).

**P1-02**: D16 wrong enforcement point. `spawn-team.sh` is optional convenience tooling. Actual Stage 6/13 cross-review runs through `cross-review.sh` and `stage5-plan-dispatch.sh`. Codex unavailability probe must live in `cross-review.sh`.

**P1-03**: D8 conflicts with existing verifier semantics. `verify-gate-evidence.py:check_plan_publish_predates_approval()` already checks this. Adding only in `exit_stage.py` creates two canonical paths that will diverge. Must reconcile into one canonical check.

## P2 Findings

**P2-01**: `stage_exit_checks.py` extraction only works if `_heavy_stage_check` and existing logic actually moves out of `exit_stage.py`, not just duplicated.

**P2-02**: `--json` flag under-specified. Does it combine with `--stage5-check`/`--stage7-check`/`--stage17-check`? Does it change exit codes? Must specify stdout-only contract + mode compatibility.

**P2-03**: D11 incomplete. `orchestrator_agent='unknown'` and `best_fit_provider='unknown'` also need blocking. Plan only addresses `session_id`.

**P2-04**: L3 schema validator has no enforcement callsite. Must wire into a hook or gate script or declare diagnostic-only.

**P2-05**: D12 WARN-only violates conditional-pause contract in `stage-gate-policy.yaml`. Must block automatic advancement.

## P3 Notes
- D7 overlaps `verify-gate-evidence.py:check_browser_open_elapsed_time()` — reuse helpers.
- Shell scripts must stay repo-rooted — avoid `$HOME/.claude` path assumptions.
- T31-T46 numbering implies 16 tests; 48/48 implies 3×16. Clarify per-provider assertion model.
