---
name: crossprovider codex capability-contracts-must-match-test-implementat
description: Capability contracts must match test/implementation dependencies
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, scheduling, dependencies, contract-enforcement]
---

Declared runtime capabilities (e.g., `requires: [bash, gh]`) must include all dependencies actually used in tests and code. If tests invoke `jq`, it must be declared in scheduled-task capabilities. Mismatch between declared and actual dependencies breaks test validity and deployment readiness.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
