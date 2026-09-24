---
name: crossprovider gemini persistence-test-coverage-scales-with-state-comp
description: Persistence test coverage scales with state complexity
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [test-design, coverage, complexity-scaling]
---

Concurrent/stateful systems need 16+ tests (not 5) covering: happy path, missing/corrupt state, concurrent access, dry-run behavior, migrations, and verification. Each layer (capture, query, index, migrate) needs separate test suites.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
