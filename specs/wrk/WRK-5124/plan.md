# WRK-5124 Plan: Fix Stage 6 cross-review gate stall for Codex/Gemini

> Merged plan: Claude draft + Codex refinements. Gemini timed out (exit 124).

## Problem

`cross-review.sh:57` calls `uv run --no-project python verify-gate-evidence.py --stage5-check`
before any provider-specific code runs. This can hang or fail for non-Claude providers,
blocking them from ever reaching their submission scripts.

Failure surface includes: missing `uv`, missing `timeout`, malformed config, broken `uv`.

## Fix — 2 Files

### 1. `scripts/review/cross-review.sh` (lines 44-70)

Replace the gate check block with guarded execution:

```bash
# Before gate check — verify uv is available
if ! command -v uv >/dev/null 2>&1; then
  echo "✖ uv not found — required for Stage 5 gate check" >&2
  exit 2
fi

# Resolve timeout command (timeout → gtimeout → none with warning)
TIMEOUT_CMD=""
if command -v timeout >/dev/null 2>&1; then
  TIMEOUT_CMD="timeout"
elif command -v gtimeout >/dev/null 2>&1; then
  TIMEOUT_CMD="gtimeout"
else
  echo "⚠ Neither timeout nor gtimeout found — running gate check without timeout guard" >&2
fi

# Read timeout from gate config (default 30s, validate as positive integer)
GATE_CONFIG="${WS_HUB_ROOT}/scripts/work-queue/stage5-gate-config.yaml"
checker_timeout=$(grep -m1 'checker_timeout:' "$GATE_CONFIG" 2>/dev/null | awk '{print $2}')
if ! [[ "${checker_timeout:-}" =~ ^[1-9][0-9]*$ ]]; then
  checker_timeout=30
fi

# Run with timeout to prevent hangs (or without if no timeout command)
stage5_exit=0
if [[ -n "$TIMEOUT_CMD" ]]; then
  stage5_output="$($TIMEOUT_CMD "${checker_timeout}s" uv run --no-project python "$STAGE5_CHECKER" \
      --stage5-check "$WRK_ID" 2>&1)" || stage5_exit=$?
else
  stage5_output="$(uv run --no-project python "$STAGE5_CHECKER" \
      --stage5-check "$WRK_ID" 2>&1)" || stage5_exit=$?
fi

# Handle timeout (exit 124) distinctly from checker failures
if [[ "$stage5_exit" -eq 124 ]]; then
  echo "✖ Stage 5 gate check TIMED OUT after ${checker_timeout}s for ${WRK_ID}" >&2
  echo "Check uv environment and verify-gate-evidence.py availability." >&2
  exit 2
elif [[ "$stage5_exit" -eq 1 ]]; then
  echo "✖ Stage 5 evidence gate FAILED (predicate failure) for ${WRK_ID}:" >&2
  echo "$stage5_output" >&2
  echo "Complete Stage 5 interactive review and evidence before Stage 6 cross-review." >&2
  exit 1
elif [[ "$stage5_exit" -ne 0 ]]; then
  echo "✖ Stage 5 evidence gate FAILED (infrastructure failure, exit $stage5_exit) for ${WRK_ID}:" >&2
  echo "$stage5_output" >&2
  echo "Repair the Stage 5 gate infrastructure before proceeding." >&2
  exit 2
fi
```

### 2. `scripts/review/submit-to-gemini.sh` (before line 139)

Add strict `check_uv_readiness()` — fails when uv missing OR broken:

```bash
check_uv_readiness() {
  if ! command -v uv >/dev/null 2>&1; then
    echo "# ERROR: uv not found" >&2
    echo "# Diagnose: command -v uv" >&2
    return 1
  fi
  # Wrap probe in timeout to prevent hanging (P2-2 fix)
  local timeout_cmd=""
  command -v timeout >/dev/null 2>&1 && timeout_cmd="timeout 10s"
  command -v gtimeout >/dev/null 2>&1 && timeout_cmd="gtimeout 10s"
  if ! $timeout_cmd uv run --no-project python -c "print(1)" >/dev/null 2>&1; then
    echo "# ERROR: uv is installed but not functional" >&2
    echo "# Diagnose: uv run --no-project python -c \"print(1)\"" >&2
    return 1
  fi
  return 0
}

check_uv_readiness || { echo "✖ uv readiness check failed — cannot render Gemini output" >&2; exit 1; }
```

### 3. No changes to `submit-to-codex.sh`

Already has `check_uv_readiness()` at line 182.

## Acceptance Criteria

1. `cross-review.sh` fails fast (exit 2) when `uv` missing
2. `cross-review.sh` falls back to `gtimeout` on macOS; warns if neither available
3. `cross-review.sh` uses validated timeout from config (default 30s)
4. `cross-review.sh` exits 2 with TIMED OUT on timeout (124)
5. `cross-review.sh` preserves checker exit 1 (predicate) vs exit 2+ (infrastructure) distinctly
6. `submit-to-gemini.sh` checks uv readiness with timeout-wrapped probe
7. Happy path unchanged for all three providers

## Test Plan

| # | Scenario | Type | Expected |
|---|----------|------|----------|
| 1 | Gate check, uv + timeout available, Stage 5 evidence present | happy | Exit 0 → proceeds |
| 2 | Gate check, uv not in PATH | error | Exit 2 + "uv not found" |
| 3 | Gate check, neither timeout nor gtimeout | edge | Warning + runs without timeout |
| 4 | Gate check exceeds configured timeout | edge | Exit 2 + "TIMED OUT" |
| 5 | Gate config missing or malformed checker_timeout | edge | Uses default 30 |
| 6 | Stage 5 checker returns exit 1 (predicate) | error | Exit 1 + predicate failure msg |
| 7 | Stage 5 checker returns exit 2+ (infra) | error | Exit 2 + infrastructure msg |
| 8 | Gemini render, uv missing | error | Exit 1 + "uv not found" |
| 9 | Gemini render, uv broken/hanging | error | Exit 1 + "not functional" (10s timeout) |

## Risk

Low — targeted changes to error handling paths. No functional changes to the happy path.

## Cross-Review Revisions (Stage 6)

P2 findings from Claude cross-review, all addressed:
- **P2-1**: Added explicit else-branches for non-timeout checker failures (exit 1 vs exit 2+)
- **P2-2**: Wrapped uv readiness probe in `timeout 10s` to prevent self-hang
- **P2-3**: Added `gtimeout` fallback + warning-only if neither available

## Plan Confirmation

confirmed_by: vamsee
confirmed_at: 2026-03-23T00:00:00Z
decision: passed
