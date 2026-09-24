---
name: crossprovider codex pre-commit-pre-push-hooks-rewrite-generated-file
description: Pre-commit/pre-push hooks rewrite generated files (coverage-results.json, pytest cache)
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git-hooks, side-effects, generated-files]
---

Workspace-hub hooks have side effects that rewrite unrelated generated files outside issue scope (e.g., `scripts/testing/coverage-results.json`, `.pytest_cache/`). Check worktree after hook runs and clean these artifacts before staging/pushing to keep branches scoped.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
