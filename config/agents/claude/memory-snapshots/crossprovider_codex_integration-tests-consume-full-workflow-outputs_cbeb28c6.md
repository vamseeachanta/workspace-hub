---
name: crossprovider codex integration-tests-consume-full-workflow-outputs
description: Integration tests consume full workflow outputs
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, integration-tests, test-design]
---

Analytics/evaluator tests should consume output from a real full `run_matrix()` call, not handbuilt synthetic frames. Synthetic fixtures miss API contract mismatches and integration gaps that the real workflow exposes.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
