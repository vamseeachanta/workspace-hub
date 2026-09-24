---
name: crossprovider codex integration-tests-require-unit-orchestration-cli
description: Integration tests require unit + orchestration + CLI layers
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing-patterns, orchestration]
---

Issue #809: Job unit tests and scheduler tests passed; DataScheduler.run_once() with real job registration wasn't tested and failed end-to-end. Test the actual scheduler entry point and CLI dispatch with real names.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
