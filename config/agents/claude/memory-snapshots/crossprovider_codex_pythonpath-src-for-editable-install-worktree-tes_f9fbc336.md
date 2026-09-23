---
name: crossprovider codex pythonpath-src-for-editable-install-worktree-tes
description: PYTHONPATH=src for editable install worktree testing
metadata:
  type: reference
  source: codex
  bridged: 2026-07-29
  tags: [editable-install, environment, testing, pythonpath]
---

When a worktree uses an editable install pointing to main checkout, set PYTHONPATH=src for direct probes to ensure the worktree version is imported; pytest handles this through repo config but direct imports need explicit override.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
