---
name: crossprovider codex tdd-gate-tests-use-minimal-fixtures-without-full
description: TDD gate tests use minimal fixtures without full artifact dependency
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [testing, TDD, test-isolation, fixture-design]
---

Design gate enforcement tests to call check_agent_log_gate() directly via Python (not through full verifier pipeline), using only minimal fixture log-directory structure (.claude/work-queue/logs/). This enables fast test iteration and isolates gate logic from artifact setup.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
