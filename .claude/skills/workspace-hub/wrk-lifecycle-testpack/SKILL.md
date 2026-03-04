---
name: wrk-lifecycle-testpack
description: >
  Reusable TDD harness for WRK lifecycle compliance. Verifies that close and
  archive are blocked unless required gate evidence and integrated/repo tests
  are present.
version: 1.0.0
updated: 2026-03-03
category: workspace-hub
triggers:
  - lifecycle testpack
  - wrk workflow tests
  - gatepass tests
related_skills:
  - workspace-hub/workflow-gatepass
  - coordination/workspace/work-queue
  - workspace-hub/qa-closure
capabilities:
  - lifecycle-compliance-testing
  - gate-bypass-negative-tests
  - close-readiness-tests
requires:
  - scripts/work-queue/verify-gate-evidence.py
invoke: wrk-lifecycle-testpack
---
# WRK Lifecycle Testpack

Use this skill when implementing or validating WRK workflow behavior.

## Test Suite Contract

Minimum test suite per workflow change:

1. Missing gate evidence fails verification.
2. Missing plan approval evidence fails verification.
3. Missing integrated/repo test evidence fails verification.
4. Integrated/repo test count outside `3-5` fails verification.
5. Full valid evidence pack passes verification.

## Required Test Data Shape

`execute.yaml` must include:
- `integrated_repo_tests` list
- each test has `name`, `scope`, `command`, `result`, `artifact_ref`
- `scope` in `integrated|repo`
- `result` in `pass|passed`

## Recommended Commands

```bash
uv run --no-project pytest -q tests/unit/test_verify_gate_evidence.py
uv run --no-project pytest -q tests/unit/test_generate_html_review.py
bash tests/work-queue/test-lifecycle-gates.sh
```

Add or update test files whenever gate contracts change.
