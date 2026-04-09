# Session Governance — Phase 2 Runtime Enforcement

> Date: 2026-04-09 | Issues: #1839, #1857 | Terminal: 4

## What Was Implemented

### 1. Runtime Session Limit Enforcement (#1839)

**File**: `scripts/workflow/session_governor.py`

Added `check_session_limits()` — a function that evaluates live session metrics against
governance-checkpoints.yaml thresholds and returns structured verdicts:

- **CONTINUE**: metric below 80% of threshold
- **PAUSE**: metric at 80-99% of threshold (warning zone)
- **STOP**: metric at or above threshold (hard stop)

Two runtime gates are now enforceable:

| Gate | Threshold | What It Does |
|------|-----------|--------------|
| `tool-call-ceiling` | 200 calls | Prevents runaway sessions (6.1M wasted calls evidence) |
| `error-loop-breaker` | 3 consecutive | Stops retry loops on repeated identical errors |

**CLI usage** (callable from hooks or Hermes):
```bash
# Check if session should continue
uv run scripts/workflow/session_governor.py --check-limits --tool-calls 150
# Returns JSON: {"verdict": "CONTINUE", "checks": [...]}

# At threshold — returns exit code 2
uv run scripts/workflow/session_governor.py --check-limits --tool-calls 200
# Returns JSON: {"verdict": "STOP", "checks": [...]}

# Warning zone — returns exit code 1
uv run scripts/workflow/session_governor.py --check-limits --tool-calls 170 --consecutive-errors 2
# Returns JSON: {"verdict": "PAUSE", "checks": [...]}
```

Exit codes: 0=CONTINUE, 1=PAUSE, 2=STOP.

### 2. Queue Staleness Detection + Parity Check (#1857)

**File**: `scripts/refresh-agent-work-queue.py`

Added two verification modes:

**Staleness detection** (`--check-staleness`):
- Reads the queue file's "Last refresh" timestamp
- Reports stale if older than 7 days
- Exit code: 0=fresh, 1=stale

**Parity check** (`--parity-check`):
- Queries live GitHub issue counts per agent
- Compares against counts in the existing queue file
- Reports which agents have drifted and by how much
- Exit code: 0=parity, 1=drift detected

Both modes output JSON for machine consumption.

### 3. Tests

| File | New Tests | Coverage |
|------|-----------|----------|
| `tests/work-queue/test_session_governor.py` | 11 tests | Runtime enforcement verdicts, thresholds, edge cases |
| `tests/work-queue/test_queue_refresh.py` | 7 tests | Staleness detection, parity check, missing file handling |

## Files Changed

| File | Change |
|------|--------|
| `scripts/workflow/session_governor.py` | Added `check_session_limits()`, `session_limits_verdict()`, `format_limits_report()`, `--check-limits` CLI |
| `scripts/refresh-agent-work-queue.py` | Added `check_staleness()`, `parity_check()`, `--check-staleness`, `--parity-check` CLI |
| `scripts/refresh-agent-work-queue.sh` | Updated to pass through new flags without staging |
| `tests/work-queue/test_session_governor.py` | 11 new runtime enforcement tests |
| `tests/work-queue/test_queue_refresh.py` | 7 new staleness/parity tests |

## What Remains

### Phase 2 follow-ups (not in this session)
- Wire `check_session_limits` into Claude Code hooks (PreToolUse or periodic check)
- Wire into Hermes session orchestrator for automatic pause/resume
- Add session-duration ceiling gate to governance-checkpoints.yaml

### Phase 3-4 (per #1839 roadmap)
- Rebuild `session-start-routine` skill
- Create `session-corpus-audit` skill
- Hermes gate transition management

## Verification Commands

```bash
# Run session governor tests
uv run --no-project python -m pytest tests/work-queue/test_session_governor.py -v

# Run queue refresh tests
uv run --no-project python -m pytest tests/work-queue/test_queue_refresh.py -v

# Smoke test: check session limits
uv run scripts/workflow/session_governor.py --check-limits --tool-calls 50
uv run scripts/workflow/session_governor.py --check-limits --tool-calls 200

# Smoke test: check queue staleness
uv run scripts/refresh-agent-work-queue.py --check-staleness
```
