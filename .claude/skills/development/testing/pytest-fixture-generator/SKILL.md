---
name: pytest-fixture-generator
description: Generate standardized pytest configuration with fixtures, markers, and
  coverage settings. Creates conftest.py and pytest.ini for workspace-hub compliant
  testing.
version: 1.0.0
category: development
type: skill
trigger: manual
auto_execute: false
capabilities:
- pytest_configuration
- fixture_generation
- coverage_setup
- marker_configuration
- path_management
tools:
- Write
- Read
- Bash
related_skills:
- python-project-template
requires: []
tags: []
---

# Pytest Fixture Generator

## Quick Start

```bash
# Generate pytest configuration
/pytest-fixture-generator

# Generate with specific markers
/pytest-fixture-generator --markers unit,integration,slow

# Generate for specific module structure
/pytest-fixture-generator --src-path src/modules
```

## When to Use

**USE when:**
- Setting up new Python project testing
- Standardizing existing test configuration
- Adding fixtures for data processing projects
- Configuring coverage requirements

**DON'T USE when:**
- Non-Python projects
- Tests already fully configured
- Different testing framework needed

## Prerequisites

- Python 3.9+
- pytest>=7.4.0
- pytest-cov>=4.1.0
- Project with src/ structure

## Overview

Generates complete pytest configuration including:

1. **pytest.ini** - pytest configuration with markers
2. **conftest.py** - Shared fixtures and path setup
3. **Coverage config** - .coveragerc or pyproject.toml
4. **Test templates** - Example test files

## Generated Files

### pytest.ini

```ini
[pytest]
testpaths = tests
python_files = test_*.py *_test.py
python_classes = Test*
python_functions = test_*

# Markers for test categorization
markers =
    unit: Unit tests (fast, isolated)

*See sub-skills for full details.*
### conftest.py

```python
"""
ABOUTME: Pytest configuration and shared fixtures for testing
ABOUTME: Provides path setup, common fixtures, and test utilities
"""

import sys
from pathlib import Path
from typing import Any, Dict, Generator
import pytest

*See sub-skills for full details.*
### Example Test File

```python
"""
ABOUTME: Example test file demonstrating pytest patterns
ABOUTME: Shows usage of fixtures and markers
"""

import pytest


class TestExampleUnit:

*See sub-skills for full details.*

## Common Fixtures Reference

| Fixture | Scope | Purpose |
|---------|-------|---------|
| `project_root` | session | Project root path |
| `data_dir` | session | Data directory path |
| `test_data_dir` | session | Test fixtures path |
| `temp_output_dir` | function | Temporary output |
| `sample_dict` | function | Sample dictionary |
| `sample_dataframe` | function | Sample DataFrame |
| `sample_time_series` | function | Time series data |
| `temp_config` | function | Temp YAML config |
| `temp_csv` | function | Temp CSV file |

## Marker Reference

| Marker | Purpose | Example |
|--------|---------|---------|
| `@pytest.mark.unit` | Unit tests | Fast, isolated |
| `@pytest.mark.integration` | Integration tests | External resources |
| `@pytest.mark.slow` | Slow tests | > 1 second |
| `@pytest.mark.skip` | Skip test | Not ready |
| `@pytest.mark.xfail` | Expected failure | Known bug |
| `@pytest.mark.parametrize` | Multiple inputs | Test matrix |

## Related Skills

- [python-project-template](../python-project-template/SKILL.md) - Full project setup
- [repo-readiness](../repo-readiness/SKILL.md) - Verify test configuration

## References

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-cov Documentation](https://pytest-cov.readthedocs.io/)
- [Testing Framework Standards](../../../docs/modules/standards/TESTING_FRAMEWORK_STANDARDS.md)

---

## Version History

- **1.0.0** (2026-01-14): Initial release - standardized pytest configuration with fixtures, markers, and coverage

## Sub-Skills

- [Example 1: Generate Basic Configuration (+2)](example-1-generate-basic-configuration/SKILL.md)
- [Best Practices](best-practices/SKILL.md)

## Sub-Skills

- [Execution Checklist](execution-checklist/SKILL.md)
- [Error Handling](error-handling/SKILL.md)
