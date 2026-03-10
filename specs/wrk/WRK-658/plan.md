# Plan: WRK-658 — Enforce Gate + Logging Contract for Every AI Agent

## Goal

Extend the gate and logging contract (established in WRK-656/657 for Claude) to cover
all AI agents (Codex, Gemini). Every agent-driven WRK run must emit start/stop log
entries, and `verify-gate-evidence.py` must fail when those logs are missing.

## Background

The logging infrastructure already exists:
- `scripts/work-queue/log-gate-event.sh` — appends YAML blocks to
  `.claude/work-queue/logs/WRK-NNN-{stage}.log`
- `log_gate_event_if_available()` in `scripts/agents/lib/workflow-guards.sh` — called
  by all 5 wrappers
- `check_agent_log_gate()` in `verify-gate-evidence.py` — enforces log presence

Gaps: no CODEX.md/GEMINI.md adapter files; provider shims unverified; gate contract
doc not updated for multi-agent scope.

## Phases

### Phase 1 — Adapter Files + Provider Shim Verification

1. Create `CODEX.md` (≤20 lines) — states gate+logging contract applies to Codex;
   mandates calling `/work run` wrappers; references `.claude/docs/orchestrator-gate-contract.md`
2. Create `GEMINI.md` (≤20 lines) — same for Gemini
3. Verify `scripts/agents/providers/codex.sh` emits log-gate-event calls before/after
   dispatch; add if missing
4. Verify `scripts/agents/providers/gemini.sh` — same

### Phase 2 — Doc Update

5. Update `.claude/docs/orchestrator-gate-contract.md` to:
   - explicitly state the contract applies to Claude, Codex, and Gemini
   - reference log path format `.claude/work-queue/logs/WRK-NNN-{stage}.log`
   - document the Bash bypass risk (gate_check.py Write hook doesn't catch Bash writes)
     and mitigation (log-gate-event.sh as fallback enforcement)
6. Update `AGENTS.md` reference line to cite `orchestrator-gate-contract.md`

### Phase 3 — TDD / Sandbox Validation

7. Write tests in `scripts/agents/tests/` that:
   - confirm CODEX.md and GEMINI.md exist and reference the contract
   - confirm `providers/codex.sh` and `providers/gemini.sh` contain log-gate-event calls
   - confirm `verify-gate-evidence.py` fails when logs are missing for a provider run
8. Run sandbox: invoke each provider wrapper (Claude, Codex, Gemini) against a test WRK
   directory and confirm logs are written; capture output in test evidence

## Verification Approach

- ≥3 tests PASS, 0 FAIL in `ac-test-matrix.md`
- Tests are deterministic (file-existence + grep-pattern checks)
- No live AI calls required for TDD phase — test against file fixtures

## Files Changed

| File | Change |
|------|--------|
| `CODEX.md` | CREATE — gate contract adapter (≤20 lines) |
| `GEMINI.md` | CREATE — gate contract adapter (≤20 lines) |
| `scripts/agents/providers/codex.sh` | VERIFY/EXTEND — add log-gate-event calls |
| `scripts/agents/providers/gemini.sh` | VERIFY/EXTEND — add log-gate-event calls |
| `.claude/docs/orchestrator-gate-contract.md` | UPDATE — multi-agent scope |
| `AGENTS.md` | UPDATE — reference to gate contract doc |
| `scripts/agents/tests/test-provider-logging.sh` | CREATE — TDD tests |

## Tests / Evals

| Test | Scenario | Expected Outcome |
|------|----------|-----------------|
| T1 | CODEX.md and GEMINI.md exist at workspace root | Files present, ≤20 lines, contain gate mandate text |
| T2 | providers/codex.sh contains log-gate-event.sh call | grep confirms log-gate-event invocation present |
| T3 | providers/gemini.sh contains log-gate-event.sh call | grep confirms log-gate-event invocation present |
| T4 | verify-gate-evidence.py fails for missing provider logs | Script exits non-zero when WRK log dir is empty |
| T5 | orchestrator-gate-contract.md references all 3 agents | grep confirms Codex, Gemini, Claude all mentioned |

## Acceptance Criteria

- [ ] CODEX.md and GEMINI.md exist at workspace root, ≤20 lines, gate mandate present
- [ ] providers/codex.sh and providers/gemini.sh emit log-gate-event entries
- [ ] verify-gate-evidence.py fails for missing provider logs
- [ ] orchestrator-gate-contract.md covers all 3 agents, references log path format
- [ ] ≥3 TDD tests PASS, 0 FAIL
