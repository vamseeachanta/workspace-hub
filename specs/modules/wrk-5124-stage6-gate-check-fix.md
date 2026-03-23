# WRK-5124: Fix Stage 6 cross-review gate stall for Codex/Gemini

## Mission

Fix the Stage 5 gate check in `cross-review.sh` that stalls for non-Claude providers due to `uv` execution path differences, and add uniform uv pre-checks across all provider submission scripts.

## Root Cause

`cross-review.sh:57` calls `uv run --no-project python verify-gate-evidence.py --stage5-check` before provider-specific code. When this hangs or fails for Codex/Gemini environments, the process stalls at the gate — never reaching submission.

## Acceptance Criteria

1. Stage 6 cross-review completes for Codex provider without stalling in gate check
2. Stage 6 cross-review completes for Gemini provider without stalling in gate check
3. Gate check handles `uv` unavailability with a clear error (not a hang)
4. All three providers have consistent uv availability checks

## Plan

### Phase 1: Fix `cross-review.sh` gate check (line 44-70)

- Add a `uv` availability pre-check with timeout before calling `verify-gate-evidence.py`
- Wrap the `uv run` call with a timeout (e.g., 30s from `stage5-gate-config.yaml`)
- If `uv` is unavailable, exit 2 with a clear diagnostic message instead of hanging

### Phase 2: Add uv pre-check to `submit-to-gemini.sh`

- Add `check_uv_readiness()` function matching `submit-to-codex.sh:182-190` pattern
- Call it before the render step

### Phase 3: Add timeout to gate checker invocation

- Use `timeout` command around the `uv run` call in `cross-review.sh`
- Respect `checker_timeout: 30` from `stage5-gate-config.yaml`

## Pseudocode

```bash
# cross-review.sh — Phase 1 fix
check_uv_available() {
  command -v uv >/dev/null 2>&1 || { echo "✖ uv not found"; exit 2; }
  uv --version >/dev/null 2>&1 || { echo "✖ uv not functional"; exit 2; }
}

# Before gate check
check_uv_available
timeout_sec=$(grep 'checker_timeout' "$GATE_CONFIG" | awk '{print $2}')
stage5_output="$(timeout "${timeout_sec:-30}s" uv run --no-project python ...)" || stage5_exit=$?
if [[ "$stage5_exit" -eq 124 ]]; then
  echo "✖ Stage 5 gate check TIMED OUT after ${timeout_sec}s" >&2
  exit 2
fi
```

## Test Plan

| Test | Type | Expected |
|------|------|----------|
| Gate check with uv available, Stage 5 evidence present | happy | Exit 0, proceeds to submission |
| Gate check with uv unavailable | error | Exit 2 with clear "uv not found" message, no hang |
| Gate check exceeds timeout | edge | Exit 2 with "TIMED OUT" message |
| Gemini submission with uv unavailable | error | Clean exit with diagnostic before render attempt |

## Files Changed

1. `scripts/review/cross-review.sh` — add uv pre-check + timeout wrapper
2. `scripts/review/submit-to-gemini.sh` — add `check_uv_readiness()` function
3. (optional) `scripts/review/submit-to-codex.sh` — no changes needed, already has check

## Scripts to Create

None — all changes are to existing scripts.
