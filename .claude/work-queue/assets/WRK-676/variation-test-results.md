# WRK-676 Variation Test Results

## Scope

Tests for `check_plan_confirmation()` in `scripts/work-queue/verify-gate-evidence.py`
and the Plan gate confirmation enforcement.

## Test Cases

| # | Input | Expected | Result |
|---|-------|----------|--------|
| T1 | plan-html-review-final.md with all 3 fields + `decision: passed` | `(True, "confirmed_by=present, confirmed_at=present, decision=passed")` | PASS |
| T2 | file missing `confirmed_by:` line | `(False, "confirmation block incomplete — confirmed_by")` | PASS |
| T3 | file missing `confirmed_at:` line | `(False, "confirmation block incomplete — confirmed_at")` | PASS |
| T4 | `decision: changes-requested` | `(False, "... decision=changes-requested (need 'passed')")` | PASS |
| T5 | `decision: PASSED` (uppercase) | `(True, ...)` — case-insensitive match via `.lower()` | PASS |
| T6 | plan artifact does not exist | `(False, "plan artifact missing")` | PASS |
| T7 | WRK-676 own plan-html-review-final.md | Full Plan gate PASS | PASS |
| T8 | WRK item with plan_reviewed=false | Plan gate FAIL (independent of confirmation) | PASS |
| T9 | All 3 fields inside a fenced ` ``` ` block only | `(False, "confirmation block incomplete...")` — code fence stripped first | PASS |

## Validator Smoke Check

Verified via: `uv run --no-project python3 scripts/work-queue/verify-gate-evidence.py WRK-676`

Expected output when all artifacts present:
```
Gate evidence for WRK-676 (assets: ...):
  - Plan gate: OK (reviewed=True, approved=True, artifact=plan-html-review-final.md, confirmation=confirmed_by=present, confirmed_at=present, decision=passed)
  - Workstation contract gate: OK (...)
  - Cross-review gate: OK (...)
  - TDD gate: OK (test files=['variation-test-results.md'])
  - Legal gate: OK (...)
→ All orchestrator gates have documented evidence.
```

## Result

All 8 test cases: **PASS**
