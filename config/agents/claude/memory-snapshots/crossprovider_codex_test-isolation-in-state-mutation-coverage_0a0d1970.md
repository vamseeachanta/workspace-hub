---
name: crossprovider codex test-isolation-in-state-mutation-coverage
description: Test isolation in state-mutation coverage
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [testing, tdd, isolation]
---

When a test mutates multiple independent state properties and asserts on a combined outcome, changes to individual components can mask failures. Split into isolated tests per property (one test for locked-status promotion, one for blocked-flow drift, one for role promotion) so each mutation path has independent verification.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
