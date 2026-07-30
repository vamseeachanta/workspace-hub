---
name: crossprovider codex settings-scope-split-repo-tracked-vs-machine-loc
description: Settings scope split: repo-tracked vs machine-local
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [configuration, git, portability]
---

`.claude/settings.json` travels via Git (repo-scoped), `.local.json` stays machine-local (gitignored). For parent-scope settings, use dedicated tracked source + single-file symlink with idempotent installer. Never symlink whole `.claude` directory or point parent settings at workspace-hub-specific hooks.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
