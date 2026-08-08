---
name: crossprovider codex test-pytest-configs-with-o-flags-instead-of-edit
description: Test pytest configs with `-o` flags instead of editing worktree
metadata:
  type: reference
  source: codex
  bridged: 2026-08-07
  tags: [pytest, testing-technique, worktree-hygiene]
---

Use `pytest -o norecursedirs=... -o ...` to test different configs without modifying a dirty checkout. This keeps measurements clean and non-destructive when verifying mechanism behavior.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
