---
name: crossprovider codex test-fixtures-must-mirror-real-execution-paths
description: Test fixtures must mirror real execution paths
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, test-design, fixture-layout, integration-testing]
---

When a test claims to cover feature X (e.g., baseline suppression in pre-commit), ensure the fixture layout and invocation path exactly match the real implementation. Tests that pass with mock paths while production uses different paths will hide integration failures.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
