# WRK-677 Variation Test Results

**date:** 2026-03-02
**scope:** `check_claim_gate()` in `verify-gate-evidence.py` + `check_plan_confirmation()`
**runner:** `uv run --no-project python3`

## Results

| Test | Scenario | Expected | Got | Result |
|------|----------|----------|-----|--------|
| T1 | Happy path — version=1, all fields, quota=available(75%) | OK (True) | True | PASS |
| T2 | No claim-evidence.yaml (legacy item) | WARN (None) | None | PASS |
| T3 | claim-evidence.yaml present, no metadata_version (legacy schema) | WARN (None) | None | PASS |
| T4 | metadata_version=1, session_owner missing | FAIL (False) | False | PASS |
| T5 | metadata_version=1, quota_snapshot.status=rate-limited | FAIL (False) | False | PASS |
| T6 | metadata_version=1, blocking_state.blocked=true | FAIL (False) | False | PASS |
| T7 | metadata_version=1, quota_snapshot.status=unknown | OK w/WARN note | True | PASS |
| T8 | metadata_version=1, quota_snapshot.status=quota-exceeded | FAIL (False) | False | PASS |
| T9 | plan confirmation block valid (confirmed_by+at, decision=passed) | True | True | PASS |
| T10 | plan confirmation wrong decision value (rejected) | False | False | PASS |

**10/10 pass**

## Notes

- T7: `quota=unknown` returns `True` (gate passes) with `[WARN: source unavailable]` embedded in the
  detail string. The claim-evidence template documents `quota_ok: true` for both `available` and `unknown`.
  The "WARN" in the Gemini P2 resolution means "not a hard failure" — not a gate-level WARN return.
- T2/T3: Legacy items (absent or unversioned claim file) return `None` → printed as WARN, no gate failure.
- T4/T5/T6/T8: All hard-fail paths for `metadata_version: "1"` items function as specified.
