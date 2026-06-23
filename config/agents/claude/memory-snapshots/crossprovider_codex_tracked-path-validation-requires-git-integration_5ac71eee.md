---
name: crossprovider codex tracked-path-validation-requires-git-integration
description: Tracked-path validation requires git integration, not just existence + normalization
metadata:
  type: reference
  source: codex
  bridged: 2026-06-22
  tags: [git-integration, validation-layers, test-realism]
---

Checking existence + path normalization passes tests using temp files while skipping the actual requirement. Must check `git ls-files` before writes to ensure targets are tracked. Integration test with real repo state, not synthetic temp paths.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
