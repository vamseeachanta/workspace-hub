---
name: xlsx-to-python-core-principle-excel-values-test-data
description: 'Sub-skill of xlsx-to-python: Core Principle: Excel Values = Test Data.'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# Core Principle: Excel Values = Test Data

## Core Principle: Excel Values = Test Data


When an Excel spreadsheet contains a calculation with input values and computed
results, **those cell values are the test cases**. The two-pass extraction strategy:

- **Pass 1** (`data_only=True`): read computed cell values — these become `pytest.approx()` assertions
- **Pass 2** (`data_only=False`): read formula strings — these become Python function implementations

This means every spreadsheet with formulas is simultaneously a specification,
an implementation reference, AND a test fixture.
