---
name: core-tester-test-pyramid
description: 'Sub-skill of core-tester: Test Pyramid (+2).'
version: 1.0.0
category: coordination
type: reference
scripts_exempt: true
---

# Test Pyramid (+2)

## Test Pyramid


```
         /\
        /E2E\      <- Few, high-value
       /------\
      /Integr. \   <- Moderate coverage
     /----------\
    /   Unit     \ <- Many, fast, focused
   /--------------\
```

## Test Quality Metrics


| Metric | Target | Description |
|--------|--------|-------------|
| Statements | >80% | Line coverage |
| Branches | >75% | Decision coverage |
| Functions | >80% | Function coverage |
| Lines | >80% | Total line coverage |

## Test Characteristics (FIRST)


- **Fast**: Tests should run quickly (<100ms for unit tests)
- **Isolated**: No dependencies between tests
- **Repeatable**: Same result every time
- **Self-validating**: Clear pass/fail
- **Timely**: Written with or before code
