---
name: crossprovider codex pytest-updates-ignored-pycache-even-with-cache-f
description: pytest updates ignored __pycache__ even with cache flags—expect in cleanup audits
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [tooling-quirk, cleanup, hygiene]
---

Running pytest will touch ignored .pytest_cache and __pycache__ entries, creating git status noise. This is expected residue in reviews/audits that run pytest. Clean-up should preserve these as expected; they should not block work if the rest of the worktree is clean.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
