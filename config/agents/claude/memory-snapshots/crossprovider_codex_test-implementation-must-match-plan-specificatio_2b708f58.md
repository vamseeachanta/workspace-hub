---
name: crossprovider codex test-implementation-must-match-plan-specificatio
description: Test implementation must match plan specification
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, plan-verification, acceptance-criteria]
---

When a plan names specific test functions (e.g., `test_domain_maturity_gate_runs_before_creation`), verify those tests are implemented in the test file. String-based content checks (e.g., 'directory exists', 'phrase found') without the named logic gate do not fulfill the plan's intended coverage.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
