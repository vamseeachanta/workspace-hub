---
name: crossprovider codex integration-tests-must-cover-component-to-compon
description: Integration tests must cover component-to-component calls, not just fixtures
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing-practice, integration-test-gap]
---

Fixture-based unit tests (e.g., running a script on synthetic inputs) verify isolated correctness but miss integration failures (skill invoking script, script writing output consumed by next layer, persistence and read-back). When testing multi-component workflows, add integration tests that span the actual call chains.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
