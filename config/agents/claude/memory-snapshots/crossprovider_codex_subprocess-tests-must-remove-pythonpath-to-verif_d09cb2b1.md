---
name: crossprovider codex subprocess-tests-must-remove-pythonpath-to-verif
description: Subprocess tests must remove PYTHONPATH to verify real-world import behavior
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, subprocess, cli-validation]
---

A regression test that invokes the CLI via subprocess should unset PYTHONPATH (or set it to empty) to simulate real-world import resolution without the pytest config override. This catches failures where the tool works in pytest but fails in production due to missing dependencies or import paths.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
