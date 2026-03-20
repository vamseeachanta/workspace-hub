# AC3 Verification — WRK-1039

## Summary

Ran `verify-gate-evidence.py` (normal + `--json`) against 10 audit WRKs from WRK-1035
session-audit-master.md, plus regression WRK-1044 (must exit 0).

## Results

| WRK | Expected | Actual | Notes |
|-----|----------|--------|-------|
| WRK-1019 | exit=1 | exit=1 ✓ | approval ordering, sentinel values, browser elapsed |
| WRK-1020 | exit=1 | exit=1 ✓ | midnight UTC sentinel, browser elapsed, commit uniqueness |
| WRK-1026 | exit=1 | exit=1 ✓ | approval ordering, done/pending contradiction |
| WRK-1028 | exit=1 | exit=1 ✓ | sentinel values, plan publish ordering |
| WRK-1029 | exit=1 | exit=1 ✓ | browser elapsed, sentinel values |
| WRK-1030 | exit=1 | exit=1 ✓ | codex keyword missing, approval ordering |
| WRK-1031 | exit=1 | exit=1 ✓ | approval ordering, sentinel values |
| WRK-570  | exit=1 | exit=1 ✓ | codex gap (expected per plan) |
| WRK-1034 | exit=0 (planned) | exit=1 | pre-existing compliance gaps (see below) |
| WRK-1036 | exit=0 (planned) | exit=1 | pre-existing compliance gaps (see below) |
| WRK-1044 | exit=0 | exit=0 ✓ | regression — clean |

## WRK-1034 and WRK-1036 Analysis

The plan expected exit=0 for WRK-1034 and WRK-1036 as "legitimate" WRKs. After the
14 Gap checks were applied, both exit=1 due to real compliance issues present before
the hardening was implemented.

**WRK-1034 real failures (Gap detections):**
- Gap 3: browser open elapsed 0s on plan_final (min 300s required)
- Gap 6: done/pending contradiction — Stage 14 marked done but comment says "pending"
- Gap 12: all three publish commits share '6452214b' (likely placeholder)

**WRK-1036 real failures (Gap detections):**
- Gap 5: activation.yaml session_id='unknown' (sentinel value)
- Gap 4: no claim-evidence.yaml (only legacy claim.yaml)

These are genuine compliance issues, not false positives. The verifier correctly
identifies them. These WRKs pre-date the 14 gap hardening.

## Bugs Fixed During AC3 Sweep

### Bug 1: DST false positive in `_parse_iso_timestamp`

`strptime` formats with `+00:00` or `Z` created naive datetime objects. On the
dev-primary machine (CST/CDT, UTC-6), March 8 2026 is DST spring-forward day.
Timestamps in the skipped 02:00-03:00 hour were compared as local time, causing
execute (02:40 CST) to appear AFTER close-review (03:30 CDT) in UTC terms.

Fix: added `.replace(tzinfo=datetime.timezone.utc)` to all parsed timestamps.
All work-queue timestamps are UTC by convention.

### Bug 2: Stage evidence paths gate — false positive for archived WRKs

Stage-evidence.yaml records paths like `pending/WRK-NNN.md` (valid during execution
but stale after archiving). The gate failed with "path not found" for archived WRKs.

Fix: added archive/ rglob fallback — if the path's filename exists in archive/,
the check continues without flagging it as a fabrication.

## --json Mode Verification

```
uv run --no-project python scripts/work-queue/verify-gate-evidence.py WRK-1019 --json
```

Last line of stdout:
```json
{"wrk_id": "WRK-1019", "phase": "close", "pass": false, "missing": [...], "warn": [...]}
```

Exit code: 1 — correct.

## Test Coverage

- T31: `get_list_field` returns first list item (not "missing") — PASS
- T32: exit_stage.py pending/ path resolution resolves to queue root — PASS
- T33: `--json` on failing WRK produces valid JSON with pass=false — PASS
- T11-T30: all Gap 1-14 checks — PASS (from WRK-1035)
- Total: 115 passing, 1 skipped, T41 failing (WRK-1044 scope)
