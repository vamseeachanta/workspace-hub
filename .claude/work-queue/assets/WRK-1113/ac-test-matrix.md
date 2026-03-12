# WRK-1113 Acceptance Criteria Test Matrix

> Stage 12 TDD evaluation. All ACs verified against evidence.

| # | Acceptance Criterion | Test(s) | Result |
|---|---------------------|---------|--------|
| AC-1 | selection-matrix.md drafted + user-approved | specs/wrk/WRK-1113/selection-matrix.md; stage-evidence.yaml stage 5 user approved | PASS |
| AC-2 | doc-extracts/<doc-ref>.yaml per selected doc | 10 YAML files in specs/wrk/WRK-1113/doc-extracts/ | PASS |
| AC-3 | ≥1 doc-verification test per calc | test_dnv_rp_b401_doc_verified.py (33 tests), test_api_rp_1632.py (16 tests), test_iso_15589_2.py (20 tests) | PASS |
| AC-4 | All existing CP tests still PASS | 69 CP tests PASS (digitalmodel pytest run) | PASS |
| AC-5 | Gap-fill functions follow module pattern | dnv_rp_b401.py: typed sigs, SCREAMING_SNAKE constants, NumPy docstrings w/ §refs | PASS |
| AC-6 | All extracted tabular data passes legal scan | `bash scripts/legal/legal-sanity-scan.sh` → PASS | PASS |
| AC-7 | improvements-log.md captures findings | specs/wrk/WRK-1113/improvements-log.md exists | PASS |
| AC-8 | drilling_riser/ module ≥3 functions + tests | 4 modules, 13 functions, 49 doc-verified tests | PASS |
| AC-9 | Exhaustion marking applied | DNV-RP-B401, API-RP-1632, ISO15589-2 marked in ledger | PASS |
| AC-10 | query-ledger --exhausted + --domain working | tests/test_query_ledger_exhausted.py (4 tests PASS) | PASS |
| AC-11 | domain-coverage.md committed | docs/document-intelligence/domain-coverage.md committed on branch | PASS |
| AC-12 | Legal scan PASS all new code | legal-sanity-scan.sh exit 0 | PASS |

## Test Run Summary

```
digitalmodel/tests/cathodic_protection/  — 69 PASS
digitalmodel/tests/drilling_riser/       — 49 PASS
scripts/data/document-index/tests/       — 16 PASS (Phase 0 scripts)
TOTAL: 134 PASS, 0 FAIL
```

## Verdict: ALL ACs PASS
