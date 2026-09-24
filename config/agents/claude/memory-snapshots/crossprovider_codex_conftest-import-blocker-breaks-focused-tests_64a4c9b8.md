---
name: crossprovider codex conftest-import-blocker-breaks-focused-tests
description: Conftest import blocker breaks focused tests
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, environment-hazard, pytest]
---

Repository conftest.py importing unavailable dependencies (e.g., plotly) breaks focused unit test collection unless run with `--confcutdir` to bypass it. This is an environmental hazard for isolated test runs; either vendor the dependency or move non-essential imports to test-specific setup.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
