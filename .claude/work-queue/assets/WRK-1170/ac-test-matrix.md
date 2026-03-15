---
wrk: WRK-1170
stage: 12
generated: 2026-03-15
---

# AC Test Matrix — WRK-1170

| AC | Description | Status | Evidence |
|----|-------------|--------|----------|
| AC1 | All records have non-null domain | PASS | 0 nulls in index.jsonl (pre-existing) |
| AC2 | Classification accuracy validated ≥50 samples | PASS | 60 samples in evidence/classification-validation.yaml |
| AC3 | Updated domain counts in registry.yaml | PASS | registry.yaml shows 14 domains, generated 2026-03-15T22:39:08 |
| AC4 | New domains added to config.yaml taxonomy | PASS | project-management added to config.yaml domains list |
| AC5 | Incremental reclassification script exists | PASS | phase-e2-remap.py serves as incremental script |
| AC6 | "other" reduced from 9.8% to <5% | PASS | 44,705/1,033,933 = 4.3% |

## TDD Evidence

- **Test file**: `tests/data/document-index/test_phase_e2_rules.py`
- **Test count**: 26
- **All passing**: Yes
- **Coverage**: All new PATH_RULES (12), FILENAME_RULES (2), and false-positive guards (6)
