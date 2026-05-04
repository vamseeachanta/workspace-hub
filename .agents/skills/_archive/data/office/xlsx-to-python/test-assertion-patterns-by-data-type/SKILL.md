---
name: xlsx-to-python-test-assertion-patterns-by-data-type
description: 'Sub-skill of xlsx-to-python: Test Assertion Patterns by Data Type (+1).'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# Test Assertion Patterns by Data Type (+1)

## Test Assertion Patterns by Data Type


| Excel Cell Type | Python Test Pattern |
|----------------|-------------------|
| Number (float) | `assert result == pytest.approx(expected, rel=1e-6)` |
| Integer | `assert result == expected` |
| Boolean | `assert result is True/False` |
| String | `assert result == "expected_string"` |
| Date | `assert result == datetime(YYYY, M, D)` |
| Error (#REF!, #N/A) | Skip — log as extraction gap |


## Tolerance Selection


| Domain | Typical Tolerance | Rationale |
|--------|------------------|-----------|
| Structural (stress, force) | `rel=1e-4` | 4 sig figs standard in engineering |
| Geotechnical (soil params) | `rel=1e-3` | Higher uncertainty in soil data |
| Financial (currency) | `abs=0.01` | Cent-level precision |
| General engineering | `rel=1e-6` | Default — tighten if needed |
