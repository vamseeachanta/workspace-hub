# WRK-693: Fix bare python3 — uv audit across hub scripts

## Mission
Replace all bare `python3` invocations of hub `.py` scripts with `uv run --no-project python`
to ensure PyYAML and other non-stdlib deps are available in every invocation.

## Plan (Route A)

- **Audit**: `grep -rn --include="*.sh" "python3" scripts/` — categorise into fix/skip/review
- **Fix**: replace `python3 "$VAR"` with `uv run --no-project python "$VAR"` for each hub .py caller
- **Remove fallbacks**: eliminate `elif command -v python3` fallback branches in submit-to-*.sh
- **Smoke-test**: run close-item.sh --help and write-wrk-state.py --help to confirm no PyYAML error
- **Test scripts**: fix test-provider-transport.sh and test-claude-compact-bundle.sh for consistency

## Acceptance Criteria

- [x] Audit complete — hit list documented
- [x] All hub .py script callers use `uv run --no-project python`
- [x] `close-item.sh --help` runs without error
- [x] Smoke tests pass (write-wrk-state.py --help OK)
- [x] Legal scan: PASS
