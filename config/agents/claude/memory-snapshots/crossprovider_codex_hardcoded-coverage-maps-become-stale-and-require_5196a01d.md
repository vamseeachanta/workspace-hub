---
name: crossprovider codex hardcoded-coverage-maps-become-stale-and-require
description: Hardcoded coverage maps become stale and require contract testing
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, quality-tooling, contract-testing]
---

Hardcoded assumptions about which tools cover which directories diverge from reality as configs evolve. Coverage detection should be derived from actual `.pre-commit-config.yaml`, hook invocations, or repo configs, with contract tests that verify assumptions against live data.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
