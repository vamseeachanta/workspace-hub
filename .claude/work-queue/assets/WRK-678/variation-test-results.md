# WRK-678 Variation Test Results

## Scope

Tests for `check_future_work_gate()` in `scripts/work-queue/verify-gate-evidence.py`.

## Test Cases

| # | Input | Expected | Result |
|---|-------|----------|--------|
| T1 | `future-work-recommendations.md` absent | `(None, "...absent (legacy item — WARN)")` | PASS |
| T2 | File present with `WRK-679` in table | `(True, "has_wrk_refs=true")` | PASS |
| T3 | File present, table empty, `no_follow_ups_rationale: Self-contained change.` | `(True, "no_follow_ups_rationale=present")` | PASS |
| T4 | File present but no WRK-refs and empty `no_follow_ups_rationale:` | `(False, "...lists no WRKs and no_follow_ups_rationale is empty")` | PASS |
| T5 | WRK-678 own future-work-recommendations.md (refs WRK-679..681) | Full Future-work gate OK | PASS |
| T6 | `code fence` with `WRK-555` inside it — plain text has none | `(False, ...)` via `strip_code_fences()` | PASS |
| T7 | File has only `wrk_id: WRK-678` header, no follow-up table entries | `(False, ...)` — self-reference excluded via `re.sub` on `wrk_id:` line | PASS |

## Validator Smoke Check

```
uv run --no-project python3 scripts/work-queue/verify-gate-evidence.py WRK-678
```

Expected output:
```
  - Future-work gate: OK (has_wrk_refs=true)
→ All orchestrator gates have documented evidence.
```

## Result

All 6 test cases: **PASS**
