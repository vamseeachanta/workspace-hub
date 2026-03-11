# Orchestrator Gate Contract Reference

Applies to **Claude, Codex, and Gemini**. Every orchestrator must produce
validator-friendly evidence for the WRK, plan, cross-review, TDD, and legal gates
before claiming execution. `scripts/work-queue/verify-gate-evidence.py WRK-xxx`
checks these artifacts; run it (or embed it) before a WRK moves out of `pending`/`working`.

## Wrapper scripts (all providers)

Use the shared wrapper scripts — direct provider API calls bypass gate logging:
- `scripts/agents/session.sh` — session init/close
- `scripts/agents/work.sh` — /work run routing
- `scripts/agents/plan.sh` — plan draft/review
- `scripts/agents/execute.sh` — implementation
- `scripts/agents/review.sh` — cross-review

See `CODEX.md` and `GEMINI.md` at the workspace root for provider-specific guidance.

## Log schema

Every log entry written by `log-gate-event.sh` uses:
```
{timestamp: ISO8601Z, wrk_id: WRK-NNN, stage: <stage>, action: <action>, signal: <signal>, provider: <provider>}
```

## Required action names per phase (check_agent_log_gate)

| Phase | Stage | Accepted actions |
|-------|-------|-----------------|
| claim | routing | `work_wrapper_complete`, `work_queue_skill` |
| claim | plan | `plan_wrapper_complete`, `plan_draft_complete` |
| close | routing | `work_wrapper_complete`, `work_queue_skill` |
| close | plan | `plan_wrapper_complete`, `plan_draft_complete` |
| close | execute | `execute_wrapper_complete`, `tdd_eval` |
| close | cross-review | `review_wrapper_complete`, `agent_cross_review` |

Missing or incomplete logs → `check_agent_log_gate()` returns False →
`verify-gate-evidence.py` exits 1 → `claim-item.sh`/`close-item.sh` blocked.
Detection is a hard gate, not a warning.

## Evidence locations

- `.claude/work-queue/assets/WRK-<id>/plan-html-review-final.md` + `plan_reviewed`/`plan_approved` flags.
- `.claude/work-queue/assets/WRK-<id>/review.*` (html/md/results) for cross-review verdicts.
- Test files in assets folder (filename contains `test`) summarizing TDD checks.
- `.claude/work-queue/assets/WRK-<id>/legal-scan.md` with `result: pass` (or waiver).

## Close gate cross-review

Closing requires multi-agent cross-review evidence (Claude, Codex, Gemini) evaluating
execution artifacts against the approved plan. Save verdicts in `assets/WRK-<id>/review.*`
and reference in `claim-evidence.yaml`.

## NO_OUTPUT policy

Timeout/no-output results must be classified as `NO_OUTPUT`; rerun/fallback logic must
execute (Codex hard gate requires at least one successful verdict).

## Invocation guidance

- Run `verify-gate-evidence.py WRK-xxx` after generating all artifacts. Non-zero exit blocks claiming.
- `claim-item.sh` and `close-item.sh` embed the verifier call automatically.
- Document gate evidence status in `assets/WRK-<id>/claim-evidence.yaml` for auditability.
