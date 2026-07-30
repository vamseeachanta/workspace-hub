---
name: crossprovider codex partial-registry-coverage-updates-need-integrati
description: Partial-registry coverage updates need integration tests alongside unit tests
metadata:
  type: reference
  source: codex
  bridged: 2026-07-07
  tags: [registry-updates, test-architecture, integration-testing]
---

Unit arithmetic tests alone don't verify production behavior (live-loader, scheduler, sidecar generation, report limitations). Add an integration test that runs the full pipeline with the new default registry state, proving strict/default semantics remain correct and downstream reports still declare gaps.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
