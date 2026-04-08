---
title: "Test-Driven Development"
tags: [testing, tdd, pytest, quality, methodology]
sources:
  - baseline-testing-standards-doc
added: 2026-04-08
last_updated: 2026-04-08
---

# Test-Driven Development

TDD is mandatory in the workspace-hub ecosystem. Tests come before implementation, no exceptions. This is enforced as a hard gate in AGENTS.md.

## Core Principles

1. **Write tests before implementation** -- Red-Green-Refactor cycle
2. **Coverage requirements** -- minimum 80%, target 90% for critical components
3. **Quality over quantity** -- meaningful tests, not just coverage numbers

## Python Testing Standards

- **Runner**: pytest with `uv run` (never bare `python3`)
- **Configuration**: `pyproject.toml` or `pytest.ini`
- **Markers**: `@pytest.mark.unit`, `@pytest.mark.integration`, `@pytest.mark.slow`
- **Coverage**: `--cov-fail-under=80`
- **Strict mode**: `--strict-markers --strict-config`

## Test Organization

```
tests/
  unit/           # Fast, isolated, no external dependencies
  integration/    # Database, API, file system interactions
  conftest.py     # Shared fixtures
```

## Enforcement

TDD is enforced via:
- `require-tdd-pairing.sh` -- warns on unpaired test changes
- AGENTS.md hard gate: "TDD mandatory -- tests before implementation; no exceptions"
- GSD framework requires tests as part of phase verification

## Cross-References

- **Source**: [Baseline Testing Standards](../sources/baseline-testing-standards-doc.md)
- **Related concept**: [[enforcement-over-instruction]]
- **Related concept**: [[compound-engineering]]
