---
name: pytest-fixture-generator-error-handling
description: 'Sub-skill of pytest-fixture-generator: Error Handling.'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# Error Handling

## Error Handling


### Tests Not Discovered


```
Error: No tests collected

Check:
1. Test files match pattern: test_*.py
2. Test functions start with: test_
3. pytest.ini testpaths is correct
```
### Coverage Below Threshold


```
FAIL Required test coverage of 80% not reached. Total coverage: 75.00%

Options:
1. Add more tests
2. Reduce threshold temporarily
3. Exclude non-critical paths
```
