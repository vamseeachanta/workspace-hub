# Plan: WRK-658 — Enforce Gate + Logging Contract for Every AI Agent

## Goal

Extend the gate+logging contract to Codex and Gemini agents. The infrastructure
(`log-gate-event.sh`, `workflow-guards.sh`, `check_agent_log_gate()`) already works.

Gap 1: No `CODEX.md`/`GEMINI.md` — agents not directed to use wrappers.
Gap 2: `check_agent_log_gate()` has no legacy exemption — pre-WRK-658 items break.
Gap 3: `orchestrator-gate-contract.md` missing log schema and required action names per phase.
Gap 4: CODEX.md/GEMINI.md do not exist at workspace root (confirmed absent).

**No new logging infrastructure.** Log schema stays: `{timestamp, wrk_id, stage,
action, signal, provider}` as written by `log-gate-event.sh`.

**AGENTS.md at 27 lines** (over 20-line limit) — out of scope for this WRK.

## Technical Design

### check_agent_log_gate() extension

Add optional `wrk_frontmatter: dict | None = None` parameter.
When provided, apply two-tier legacy discriminator before checking logs:

```
parse id: strip 'WRK-' prefix; parse remainder as int.
if absent / non-WRK-NNN format / non-integer suffix → fail gate immediately.
if int(id_num) < 658 → return True, "legacy WRK (id < 658) — log gate skipped"
if int(id_num) >= 658:
    parse created_at from wrk_frontmatter (may be absent)
    normalize Z → +00:00 then datetime.fromisoformat() [Python 3.8+ safe]
    if absent / ValueError → fail gate (treat as new)
    CUTOFF = datetime(2026, 3, 9, tzinfo=timezone.utc)  # named constant LOG_GATE_SINCE
    if parsed_dt < CUTOFF → return True, "pre-cutoff backfill — log gate skipped"
    if parsed_dt >= CUTOFF → proceed to log entry check (existing logic)
```

When `wrk_frontmatter` is None (all current callers) → existing behavior unchanged
(backward compatible — no legacy exemption, logs required for all).

`run_checks()` passes frontmatter dict from already-loaded WRK file (no new file reads).

### Tests

All tests call `check_agent_log_gate()` directly via Python (`python -c "..."`) so
they do NOT need the full verifier artifact set. Log fixtures need only:
`{fixture_dir}/.claude/work-queue/logs/{WRK_ID}-{stage}.log`

## Phases (TDD-first)

### Phase 1 — Write 14 Failing Tests + Fixtures

Create `scripts/agents/tests/fixtures/wrk-fixture/` with minimal log fixture dirs:
- `new-wrk/.claude/work-queue/logs/` (empty) — id=WRK-700, created_at=2026-03-10T00:00:00Z
- `legacy-wrk/.claude/work-queue/logs/` (empty) — id=WRK-001 (no created_at)
- `boundary-wrk/.claude/work-queue/logs/` (empty) — id=WRK-658, created_at=2026-03-09T12:00:00Z
- `backfill-wrk/.claude/work-queue/logs/` (empty) — id=WRK-700, created_at=2026-01-01T00:00:00Z
- `valid-logs/.claude/work-queue/logs/` with log files:
  `WRK-700-routing.log`, `WRK-700-plan.log`, `WRK-700-execute.log`, `WRK-700-cross-review.log`
  (each with action matching check_agent_log_gate close-phase requirements)

Create `scripts/agents/tests/test-provider-logging.sh` with exactly **14 tests**:

| # | Test | Method | Will FAIL now? |
|---|------|--------|---------------|
| T1 | CODEX.md exists, ≤20 lines, refs wrappers + gate contract | file+wc+grep | YES |
| T2 | GEMINI.md exists, ≤20 lines, refs wrappers + gate contract | file+wc+grep | YES |
| T3 | check_agent_log_gate(valid-logs, WRK-700, close, frontmatter=new) PASSES | uv run --no-project python -c | YES (no frontmatter param) |
| T4 | check_agent_log_gate(new-wrk, WRK-700, close, frontmatter=new) FAILS | uv run --no-project python -c | YES (no frontmatter param) |
| T5 | check_agent_log_gate(legacy-wrk, WRK-001, close, frontmatter=legacy) PASSES | uv run --no-project python -c | YES (no legacy exemption) |
| T6 | check_agent_log_gate(new-wrk, WRK-700, close, at-cutoff created_at inline) FAILS | uv run --no-project python -c | YES (boundary equality test) |
| T7 | check_agent_log_gate with id=WRK-700, malformed created_at → FAILS | uv run --no-project python -c inline | YES (no discriminator) |
| T8 | check_agent_log_gate(legacy-wrk, WRK-001, no created_at) PASSES | uv run --no-project python -c | YES |
| T9 | check_agent_log_gate with id=WRK-TEST (non-numeric) → FAILS | uv run --no-project python -c inline | YES |
| T10 | orchestrator-gate-contract.md documents log schema + required action names per phase | grep | YES |
| T11 | check_agent_log_gate(backfill-wrk, WRK-700, backfill frontmatter) PASSES | uv run --no-project python -c | YES |
| T12 | check_agent_log_gate(boundary-wrk, WRK-658, boundary frontmatter) FAILS | uv run --no-project python -c | YES |
| T13 | check_agent_log_gate(legacy-wrk, WRK-001, close, wrk_frontmatter={'id':'WRK-001'}) PASSES | uv run --no-project python -c inline | YES (no wrk_frontmatter param yet) |
| T14 | get_field(parse_frontmatter(wrk_stub), 'id') returns 'WRK-001' | uv run --no-project python -c inline | YES (proves extraction helpers work) |

**T6 specification**: Uses `new-wrk` fixture (empty logs) with inline frontmatter dict
`{'id': 'WRK-700', 'created_at': '2026-03-09T00:00:00Z'}` (exactly at cutoff) → FAILS
(≥ cutoff, not <). Tests boundary equality (cutoff date is not excluded from enforcement).

**T14 specification**: Pass a raw YAML string `"---\nid: WRK-001\ncreated_at: 2026-01-01\n---\n"`
directly to `parse_frontmatter()` then `get_field()` inline. Proves the extraction helpers
used by `run_checks()` to build the `wrk_frontmatter` dict are correct.

Final bar: **14 PASS, 0 FAIL** (all mandatory).

AC-test traceability:
- AC1 (CODEX.md + GEMINI.md exist) ← T1, T2
- AC2 (check_agent_log_gate function extended with frontmatter param) ← T3, T4, T13, T14
- AC3 (legacy exemption all cases) ← T5, T7, T8, T9, T11, T12
- AC3b (boundary/cutoff equality) ← T6
- AC4 (gate-contract doc documents log schema + required action names per phase) ← T10

### Phase 2 — Make All 14 Tests Pass

1. Create `CODEX.md` (≤20 lines):
   - Use `/work run` wrappers (session.sh, work.sh, execute.sh, etc.)
   - Direct provider calls bypass gate logging — do not call providers/ directly
   - See `.claude/docs/orchestrator-gate-contract.md`

2. Create `GEMINI.md` (≤20 lines) — same content

3. Update `check_agent_log_gate()` in `verify-gate-evidence.py`:
   - Add `wrk_frontmatter: dict | None = None` parameter
   - Add `LOG_GATE_SINCE` named constant = `datetime(2026, 3, 9, tzinfo=timezone.utc)`
   - Add two-tier discriminator logic before existing log checks
   - All existing callers unaffected (None default = current behavior)
   - Add `workspace_root: Path | None = None` parameter to `run_checks()` (defaults to
     current `Path(__file__).resolve().parents[2]`); this allows fixture-based testing.
   - `run_checks()` uses existing `parse_frontmatter()` + `get_field()` helpers (regex-based,
     no PyYAML required) to extract `id` and `created_at`, then passes
     `{'id': id_val, 'created_at': created_at_val}` as `wrk_frontmatter` dict.
   - T13 (inline integration): call `check_agent_log_gate(legacy_fixture_path, 'WRK-001', 'close',
     wrk_frontmatter={'id': 'WRK-001'})` directly via `uv run --no-project python -c` and verify
     it returns True. Proves `wrk_frontmatter` param is accepted and Tier 1 legacy skip works.
   - Backward-compatible: existing CLI callers with no `workspace_root` arg unchanged.

   **WRK-658 bootstrapping note**: WRK-658 itself has `created_at: 2026-03-01T12:00:00Z`
   (< cutoff 2026-03-09T00:00:00Z) and id=WRK-658 (id_num=658). Tier 2 applies:
   valid datetime < cutoff → skip gate (backfill). WRK-658 will NOT be blocked by its
   own gate change at close time.

### Phase 3 — Doc Update

4. Update `.claude/docs/orchestrator-gate-contract.md`:
   - Applies to Claude, Codex, and Gemini
   - Single logging path: `log_gate_event_if_available()` via `workflow-guards.sh`
   - Log schema: `{timestamp, wrk_id, stage, action, signal, provider}`
   - Required actions per phase (from `check_agent_log_gate`)
   - CODEX.md/GEMINI.md are advisory harness files; bypass detectable via missing logs
   - **Enforcement**: missing/incomplete logs → `check_agent_log_gate()` returns False →
     `verify-gate-evidence.py` exits 1 → `claim-item.sh`/`close-item.sh` blocked. Detection
     is a hard gate, not a warning.

## Tests / Evals

| Test | Scenario | Expected |
|------|----------|---------|
| T1 | CODEX.md exists ≤20 lines | PASS |
| T2 | GEMINI.md exists ≤20 lines | PASS |
| T3 | check_agent_log_gate(valid-logs, close, new-frontmatter) → True | PASS |
| T4 | check_agent_log_gate(empty-logs, close, new-frontmatter) → False | PASS |
| T5 | check_agent_log_gate(empty-logs, close, legacy id<658) → True | PASS |
| T6 | check_agent_log_gate(empty-logs, close, id=WRK-700, at-cutoff) → False | PASS |
| T7 | check_agent_log_gate(malformed created_at, id≥658) → False | PASS |
| T8 | check_agent_log_gate(legacy, absent created_at) → True | PASS |
| T9 | check_agent_log_gate(id=WRK-TEST non-numeric) → False | PASS |
| T10 | gate-contract doc has log schema + required action names per phase | PASS |
| T11 | check_agent_log_gate(backfill id≥658 created_at<cutoff) → True | PASS |
| T12 | check_agent_log_gate(id=658 boundary) → False | PASS |
| T13 | check_agent_log_gate(legacy-wrk, WRK-001, close, wrk_frontmatter={'id':'WRK-001'}) PASSES | PASS |
| T14 | get_field(parse_frontmatter(stub_yaml), 'id') returns 'WRK-001' (extraction helpers correct) | PASS |

## Files Changed

| File | Change |
|------|--------|
| `scripts/agents/tests/test-provider-logging.sh` | CREATE — 14 TDD tests |
| `scripts/agents/tests/fixtures/wrk-fixture/` | CREATE — 5 fixture dirs |
| `CODEX.md` | CREATE — harness adapter (≤20 lines) |
| `GEMINI.md` | CREATE — harness adapter (≤20 lines) |
| `scripts/work-queue/verify-gate-evidence.py` | UPDATE — frontmatter param, workspace_root param for run_checks, discriminator |
| `.claude/docs/orchestrator-gate-contract.md` | UPDATE — multi-agent scope |

## Acceptance Criteria

- [ ] CODEX.md + GEMINI.md exist ≤20 lines, mandate wrapper use, ref gate contract
- [ ] `check_agent_log_gate()` has `wrk_frontmatter` param; `LOG_GATE_SINCE` named constant
- [ ] Legacy: id < 658 → skip gate; id ≥ 658, malformed created_at → fail gate
- [ ] Boundary: id=658, created_at=cutoff → enforce gate (not skip)
- [ ] `orchestrator-gate-contract.md` documents log schema (`{timestamp, wrk_id, stage, action, signal, provider}`) + required action names per phase
- [ ] 14 TDD tests: **14 PASS, 0 FAIL**
- [ ] Cross-review APPROVE (Codex hard gate)
- [ ] Legal scan PASS
- [ ] `verify-gate-evidence.py WRK-658` PASS before close
