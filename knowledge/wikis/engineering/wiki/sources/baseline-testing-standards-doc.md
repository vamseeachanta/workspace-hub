---
title: "Baseline Testing Standards (Source)"
tags: [source, testing, tdd, pytest, standards]
source_path: docs/modules/testing/baseline-testing-standards.md
source_type: module-doc
ingested: 2026-04-08
---

# Source: Baseline Testing Standards

**Path**: `docs/modules/testing/baseline-testing-standards.md`
**Version**: 1.0.0

## Summary

Universal testing standards for all repository types. Establishes TDD as mandatory, defines coverage requirements (80% minimum, 90% target), and specifies Python project testing configuration with pytest.

## Key Extractions

- **TDD mandatory**: write tests before implementation, Red-Green-Refactor
- **Coverage**: 80% minimum, 90% for critical components
- **Runner**: pytest with strict markers and config
- **Organization**: `tests/unit/`, `tests/integration/`, `conftest.py`
- **CI/CD integration**: automated execution, coverage reporting, quality gates

## Pages Created From This Source

- [Test-Driven Development](../concepts/test-driven-development.md)
