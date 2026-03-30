---
name: pytest-fixture-generator-execution-checklist
description: 'Sub-skill of pytest-fixture-generator: Execution Checklist.'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# Execution Checklist

## Execution Checklist


**Setup:**
- [ ] pytest and pytest-cov installed
- [ ] Project has src/ directory structure
- [ ] tests/ directory exists

**Generation:**
- [ ] Generate pytest.ini
- [ ] Generate conftest.py
- [ ] Create example test file
- [ ] Configure coverage

**Verification:**
- [ ] Run `pytest --collect-only` to verify discovery
- [ ] Run `pytest -v` to execute tests
- [ ] Check coverage report
