---
name: wrk-lifecycle-testpack
description: >
  Reusable TDD harness for WRK lifecycle compliance. Verifies that close and
  archive are blocked unless required gate evidence and integrated/repo tests
  are present.
version: 1.0.1
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
  - scripts/review/orchestrator-variation-check.sh
  - scripts/work-queue/parse-session-logs.sh
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

## Orchestrator Variation Tests

For cross-provider test runs (Claude / Codex / Gemini), use the shared harness:

```bash
# Run variation check for a given provider
bash scripts/review/orchestrator-variation-check.sh \
  --wrk WRK-NNN \
  --orchestrator claude \
  --scripts \
    "uv run --no-project python scripts/work-queue/verify-gate-evidence.py WRK-NNN" \
    "bash tests/work-queue/test-lifecycle-gates.sh" \
    "uv run --no-project python -m pytest tests/unit/test_circle.py -v"

# Parse session logs across all providers for a set of WRKs
bash scripts/work-queue/parse-session-logs.sh WRK-1002 WRK-1003 WRK-1004
```

`variation-test-results.md` runner field must match the orchestrator name;
`parse-session-logs.sh` handles JSONL (Claude) and plain-text (Codex/Gemini) formats.
