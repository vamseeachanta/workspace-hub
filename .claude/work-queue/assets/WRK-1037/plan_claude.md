# WRK-1037 Plan — Cross-Review Hardening

## P1-A: uv Readiness in `submit-to-codex.sh`

**Current bug** (`run_renderer`, line 188-196):
```bash
if command -v uv >/dev/null 2>&1; then
    uv run --no-project python "$RENDERER" ... && return   # && return = falls through on failure
fi
if command -v python3 >/dev/null 2>&1; then               # reached if uv present but broken
    python3 "$RENDERER" ...
fi
```

**Fix**: If `uv` is present, it is the ONLY path. A broken uv is an error, not a fallback trigger.
```bash
if command -v uv >/dev/null 2>&1; then
    uv run --no-project python "$RENDERER" --provider codex --input "$raw_file"
    return $?   # propagate exit code; never fall through to python3
fi
```

**New test** (`scripts/review/tests/test-uv-readiness.sh`):
- T1: uv present + working → renderer runs, exit 0
- T2: uv present + broken (stubbed to exit 1) → run_renderer fails, does NOT call python3
- T3: uv absent, python3 present → falls through to python3 (existing behaviour preserved)

---

## P1-B: `--allow-no-codex` Flag in `cross-review.sh`

**Current behaviour**: Codex CLI missing → hard gate fails (exit 1, "Install Codex CLI").
Already correct — no silent 2-of-3 fallback. ✓

**Gap**: No user escape hatch. Maintainers sometimes need to proceed consciously
(e.g., bootstrapping a new machine, emergency hotfix). Without a flag, there's no
policy-compliant way to proceed.

**Fix**: Add `--allow-no-codex` flag to `cross-review.sh`.
- When Codex CLI is missing AND `--allow-no-codex` is set:
  - Print explicit warning: "WARN: proceeding without Codex — reviewer override active"
  - Write a `*-CODEX-ABSENT.md` record (wrk_id, timestamp, reason placeholder)
  - Exit 0 so the pipeline can continue (user has consciously approved)
- When flag is NOT set: existing hard-fail behaviour unchanged

**New test**: `test-cross-review-codex-hardgate.sh` already exists — extend with:
- T-new: `all` mode, Codex CLI absent, no `--allow-no-codex` → exit non-zero ✓ (existing test)
- T-new: `all` mode, Codex CLI absent, `--allow-no-codex` set → exit 0 + CODEX-ABSENT.md written

---

## Implementation Order

1. Fix `run_renderer()` in `submit-to-codex.sh` (2-line change)
2. Add `--allow-no-codex` parsing + conditional branch in `cross-review.sh`
3. Write `scripts/review/tests/test-uv-readiness.sh` (T1/T2/T3)
4. Extend `test-cross-review-codex-hardgate.sh` with T-new cases
5. Run all existing tests to confirm no regressions

## Files Changed
- `scripts/review/submit-to-codex.sh` (run_renderer fix)
- `scripts/review/cross-review.sh` (--allow-no-codex flag)
- `scripts/review/tests/test-uv-readiness.sh` (new)
- `scripts/review/tests/test-cross-review-codex-hardgate.sh` (extend)

## Test Pass Criteria
All existing tests pass + new T1/T2/T3/T-new added.
