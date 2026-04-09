# Session Governance — Hard-Stop Checkpoints

> Phase 1 implementation of #1839. Provides the checkpoint model and verification utility.
> Subsequent phases add runtime enforcement via hooks and Hermes orchestration.

## What Was Implemented (Phase 1)

### 1. Machine-Readable Checkpoint Config

**File**: `scripts/workflow/governance-checkpoints.yaml`

Defines 7 session lifecycle checkpoints with:
- `type`: `hard-stop` (user must approve) or `auto-gate` (system-enforced)
- `enforced`: whether failure blocks the session (`true`) or is advisory (`false`)
- `threshold`: numeric limits for runtime gates (tool-call ceiling, error loop)

### 2. Session Governor Utility

**File**: `scripts/workflow/session_governor.py`

A verification utility that checks which gates have been satisfied:

```bash
# List all checkpoints
uv run scripts/workflow/session_governor.py --list

# Check session with specific gates passed
uv run scripts/workflow/session_governor.py --passed plan-approval tdd-red

# Check with no gates (worst case)
uv run scripts/workflow/session_governor.py
```

Exit code: `0` = all enforced gates pass, `1` = at least one enforced gate fails.

### 3. Tests

**File**: `tests/work-queue/test_session_governor.py` — 14 tests covering config loading, gate verification logic, and edge cases.

## Current Checkpoints

| ID | Name | Type | Enforced | Stage |
|----|------|------|----------|-------|
| plan-approval | Plan Approval | hard-stop | Yes | pre-implement |
| review-verdict | Review Verdict | hard-stop | Yes | post-review |
| session-close | Session Close | hard-stop | No (Phase 2) | end |
| tdd-red | TDD Red Phase | auto-gate | Yes | pre-implement |
| tool-call-ceiling | Tool Call Ceiling (200) | auto-gate | Yes | runtime |
| error-loop-breaker | Error Loop Breaker (3x) | auto-gate | Yes | runtime |
| pre-push-review | Pre-Push Review Gate | auto-gate | No (migration) | pre-push |

## What Was Implemented (Phase 2) — 2026-04-09

### Runtime Enforcement via `check_session_limits()`

**File**: `scripts/workflow/session_governor.py`

The session governor now supports runtime enforcement — checking live session metrics
against governance thresholds. Three-tier verdict system:
- **CONTINUE** (exit 0): below 80% of threshold
- **PAUSE** (exit 1): 80-99% of threshold — warning zone
- **STOP** (exit 2): at or above threshold — hard stop required

```bash
uv run scripts/workflow/session_governor.py --check-limits --tool-calls 170 --consecutive-errors 2
```

Tests: 11 new tests in `tests/work-queue/test_session_governor.py` (25 total).

### Queue Staleness + Parity Check

**File**: `scripts/refresh-agent-work-queue.py`

- `--check-staleness`: reports if queue file is >7 days old
- `--parity-check`: compares file issue counts vs live GitHub

Tests: 7 new tests in `tests/work-queue/test_queue_refresh.py` (23 total).

## What Was Implemented (Phase 2b) — 2026-04-09

### Hook Integration: `session-governor-check.sh`

**File**: `.claude/hooks/session-governor-check.sh`

A PreToolUse hook that wires `check_session_limits()` into the Claude Code session lifecycle.
Registered in `.claude/settings.json` as the first PreToolUse hook, matching all tool types.

**Architecture:**
- Maintains a per-day tool call counter in `.claude/state/session-governor/tool-call-count`
- **Fast path** (< 160 calls): pure bash counter increment, exits silently (~0ms overhead)
- **Warning zone** (160-199 calls): delegates to `session_governor.py --check-limits`, emits stderr warning
- **Ceiling** (>= 200 calls): delegates to governor, emits `{"decision":"block"}` on stdout to block further tool calls

**Protocol:** follows the repo convention from `cross-review-gate.sh` — stdout JSON for Claude context, stderr for user terminal. Always exits 0; blocking is via `{"decision":"block"}`.

**Tests:** 8 new tests in `tests/work-queue/test_session_governor.py` (33 total), covering:
- Hook file existence and executable bit
- Hook registration in settings.json
- Governor exit code mapping (0=CONTINUE, 1=PAUSE, 2=STOP)
- Fast-path threshold alignment with governance config
- CLI exit code verification via subprocess

### Known Gaps (documented, not blocked)

| Gap | Status | Resolution Path |
|-----|--------|-----------------|
| Consecutive error tracking | Passes 0 to governor | Wire into session signal pipeline (Phase 3) |
| Counter resets daily, not per-session | No reliable session ID in hook env | Awaits Claude Code session ID exposure |
| Existing `tool-call-ceiling.sh` (PostToolUse) uses 500 ceiling | Redundant safety net | Consider aligning to 200 or removing |

## What Remains (Phases 3-4)

### Phase 3: Restore Lost Infrastructure
- Rebuild `session-start-routine` skill
- Create `session-corpus-audit` skill
- Promote `comprehensive-learning` into skills tree
- Create `cross-review-policy`, `dev-workflow` skills

### Phase 4: Hermes Orchestration
- Hermes manages gate transitions and hard-stop enforcement
- Hermes dispatches to Claude/Codex/Gemini per routing matrix
- Hermes tracks session metrics and generates session reports
- Inter-session continuity validation

## References

- Issue: #1839
- Trust Architecture: `docs/governance/TRUST-ARCHITECTURE.md`
- Review Routing Policy: `docs/standards/AI_REVIEW_ROUTING_POLICY.md`
- Session failures analysis: `docs/reports/session-failures-and-refactor-review.md`
