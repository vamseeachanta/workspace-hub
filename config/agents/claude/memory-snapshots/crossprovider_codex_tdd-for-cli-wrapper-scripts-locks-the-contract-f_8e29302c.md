---
name: crossprovider codex tdd-for-cli-wrapper-scripts-locks-the-contract-f
description: TDD for CLI wrapper scripts locks the contract first
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, cli-contracts, tdd, documentation-sync]
---

Before fixing a broken CLI wrapper, test the actual CLI contract and the wrapper's invocation against a mock binary. This catches stale flag usage (e.g., nonexistent `--skill` flag) and ensures the patch matches the current CLI API, not a guessed one. Always update stale documentation references alongside code changes.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
