# WRK-325 Plan: OrcaFlex Example QA Suite

> Route C spec for `.claude/work-queue/pending/WRK-325.md`

## Problem
Without automated QA checks on representative `.sim` outputs, result quality could not be validated consistently nor consumed by downstream reporting.

## Implementation Plan
1. Implement per-example QA checks for R01-R06 with physics-based pass criteria.
2. Add JSON serialization for machine-readable per-example outcomes.
3. Generate consolidated Markdown QA summary.
4. Provide stable import surface for programmatic QA invocation.
5. Ensure graceful behavior when `.sim` artifacts are missing.

## Deliverables
- `digitalmodel/docs/domains/orcaflex/examples/qa/orcaflex_example_qa.py`
- `digitalmodel/src/digitalmodel/orcaflex/qa.py`

## Validation
- Import check: `from digitalmodel.orcaflex.qa import run_orcaflex_qa`
- QA runner emits report and JSON outputs when artifacts exist.

## Cross-Review Log
| Iter | Date | Reviewer | Verdict | Findings | Fixed |
|------|------|----------|---------|----------|-------|
| P1 | 2026-02-24 | Claude | MINOR | Import contract required explicit package-level exposure. | yes |
| P2 | 2026-02-26 | Codex | APPROVE | Facade module added and import contract now satisfied. | n/a |
| P3 | 2026-02-26 | Gemini | MINOR | Independent CLI review deferred (local CLI timeout); no unmet acceptance signal in current code. | deferred |
