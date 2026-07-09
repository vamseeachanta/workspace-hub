---
name: crossprovider codex test-all-validator-entry-paths-not-just-happy-pa
description: Test all validator entry paths, not just happy-path
metadata:
  type: reference
  source: codex
  bridged: 2026-07-01
  tags: [testing, test-gaps]
---

Indirect entry paths (request-pointer refs, evidence indirection through multiple layers) need explicit test cases separate from direct-path tests; passing the main test suite doesn't catch crashes in helper functions called by alternate entry points.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
