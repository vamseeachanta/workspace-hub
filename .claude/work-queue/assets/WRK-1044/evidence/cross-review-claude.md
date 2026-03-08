# Cross-Review — Claude (Plan Stage 6)

## Verdict: REVISE

## P1 Findings (blocking)

**P1-01**: `exit_stage.py` extraction to `stage_exit_checks.py` will NOT achieve line budget. Current 361 lines + dispatch table + imports + call sites → still ≥400. Plan must specify which functions move out (including `_heavy_stage_check`).

**P1-02**: D2 write-backstop only covers `Write` tool calls. Bash writes bypass `gate_check.py` entirely (acknowledged in existing header comment). D2 as "hard gate" must also guard canonical entrypoints (`cross-review.sh`, `claim-item.sh`, `close-item.sh`).

**P1-03**: D7/D8 fail-open condition too wide. Session audit shows browser-open yaml is PRESENT in all 10 WRKs — the violation is present yaml with inverted timestamps. Fail-open should only trigger when yaml is absent, not when timestamps are inverted (that case must be a hard FAIL).

**P1-04**: D11 sentinel check is one field only (`session_id`). R-09 requires ALL of: `session_id`, `orchestrator_agent`, `best_fit_provider`, `session_owner` ≠ "unknown", `route` ≠ "", `quota_snapshot.pct_remaining` ≠ null when status=available. Plan must either cover all or explicitly defer remainder with WRK ref.

## P2 Findings

**P2-01**: T31-T46 = 16 test IDs for 48 scenarios — ambiguous. Clarify each T3N covers 3 providers.

**P2-02**: D12 WARN with no override artifact = no enforcement. Require `cross-review-p1-override.yaml` (reviewer in allowlist + reason) before Stage 7 can proceed.

**P2-03**: `verify-gate-evidence.py` 80-line cap — pre-approve specific overage or move D9/D10 functions to `stage_exit_checks.py` instead.

## P3 Notes
- D6 Stage 19 check is late — also check at Stage 14.
- D7 overlaps existing close-time verifier checks — reuse shared helpers.
- Test count inconsistency: plan says ≥84, ACs say ≥100. Fix to ≥100.
