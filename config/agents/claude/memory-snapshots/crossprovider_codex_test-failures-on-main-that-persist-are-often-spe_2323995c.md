---
name: crossprovider codex test-failures-on-main-that-persist-are-often-spe
description: Test failures on `main` that persist are often specifications of intended behavior, not stale bugs
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [test-contracts, main-branch-state, test-repair, specifications]
---

When a test suite has known failures on the base branch, those failures often represent the current contract and the code's intended behavior. Before weakening a test to make it pass, read it carefully — it may be documenting what the code should do but does not yet. Fix the implementation to match the test, not the test to match the implementation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
