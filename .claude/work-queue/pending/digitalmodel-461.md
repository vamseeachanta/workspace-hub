---
id: digitalmodel#461
title: "Stabilize doc-intelligence launcher and pytest runtime on dev-primary"
type: standard
status: pending
priority: medium
complexity: moderate
route: A
created_at: 2026-03-23
target_repos: [workspace-hub]
computer: dev-primary
orchestrator: codex
plan_workstations: [dev-primary]
execution_workstations: [dev-primary]
category: developer-experience
subcategory: runtime-stability
parent: WRK-5127
github_issue_ref: https://github.com/vamseeachanta/digitalmodel/issues/461
blocked_by: []
---

## Mission

Stabilize the local runtime path used for targeted `uv run`, pytest, and
generator execution on `dev-primary` so document-intelligence work can be
verified without ad hoc interpreter/path workarounds.

## What

1. Reproduce the launcher/runtime instability seen during:
   - `uv run pytest tests/data/doc_intelligence/test_generate_ship_dimension_template.py`
   - direct generator execution for `generate-ship-dimension-template.py`
2. Determine whether the issue is caused by:
   - `uv` environment bootstrap
   - the local `.venv` layout
   - pytest plugin autoload / startup behavior
   - repo-local path or import side effects
3. Define the canonical working invocation for targeted tests and generators on
   this machine.
4. Remove the need for manual `PYTHONPATH` / interpreter shims if possible.
5. Document the fix and any fallback command in the relevant WRK or tooling doc.

## Acceptance Criteria

1. A targeted pytest invocation for
   `tests/data/doc_intelligence/test_generate_ship_dimension_template.py`
   completes predictably on `dev-primary`
2. The ship-dimension generator runs to completion without ambiguous stall
   behavior
3. The validated invocation path is documented for future document-intelligence
   WRKs
4. No hidden environment workaround remains required for normal local execution

## Notes

This was opened from `WRK-5127` after the artifact recovery completed but local
execution remained unstable during TDD and generator verification.
