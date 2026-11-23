---
name: pytest-fixture-generator-example-1-generate-basic-configuration
description: 'Sub-skill of pytest-fixture-generator: Example 1: Generate Basic Configuration
  (+2).'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# Example 1: Generate Basic Configuration (+2)

## Example 1: Generate Basic Configuration


```bash
# Generate for standard project
/pytest-fixture-generator

# Creates:
# - pytest.ini
# - tests/conftest.py
# - tests/test_example.py
```


## Example 2: Custom Markers


```bash
# Generate with domain-specific markers
/pytest-fixture-generator --markers unit,integration,api,database,etl
```


## Example 3: Specific Coverage Target


```bash
# Generate with 90% coverage requirement
/pytest-fixture-generator --coverage 90
```
