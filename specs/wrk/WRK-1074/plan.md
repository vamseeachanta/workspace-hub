# WRK-1074 Plan — Cross-Repo API Contracts

> Source: inline plan from .claude/work-queue/working/WRK-1074.md
> Route: B (Medium)
> Approved: 2026-03-09T15:28:00Z by vamsee

## Context
- assetutilities v0.0.8; 41 unique import sources in consumers
- digitalmodel already has `tests/contracts/` (empty dir)
- worldenergydata needs `tests/contracts/` dir created
- All repos use pytest; PYTHONPATH includes `../assetutilities/src`

## Steps

1. Shared conftest.py — `au_version()` fixture, `contracts` marker, contract violation hook
2. digitalmodel contract tests (≥3 files): data, yml, units, common
3. worldenergydata contract tests (≥2 files): data, engine
4. Failure output enrichment via `pytest_runtest_makereport` hook
5. run-all-tests.sh integration — contracts step after unit tests
6. docs/api-contracts.md per consuming repo

## Acceptance Criteria
- AC1: ≥3 contract test files in digitalmodel/tests/contracts/
- AC2: ≥2 contract test files in worldenergydata/tests/contracts/
- AC3: contract tests run in run-all-tests.sh
- AC4: failed test output shows symbol, au_version, test name
- AC5: docs/api-contracts.md per repo
- AC6: cross-review passes
