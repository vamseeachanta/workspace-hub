---
name: crossprovider codex repository-pre-push-hooks-block-on-unrelated-sib
description: Repository pre-push hooks block on unrelated sibling failures
metadata:
  type: reference
  source: codex
  bridged: 2026-07-16
  tags: [ci-cd, hooks, workflow]
---

Pre-push hooks can fail on unrelated sibling-repository build failures (e.g., sibling failing black/mypy) even for feature branches. Planning-only work shouldn't be gated by other repos' state; use scoped `--no-verify` with explicit evidence that the feature's own checks passed. Document the bypass reason and verify gate results separately.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
