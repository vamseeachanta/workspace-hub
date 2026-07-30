---
name: crossprovider codex configuration-split-symlink-installed-tracked-se
description: Configuration split: symlink-installed tracked settings vs. machine-local ignored settings
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [claude-config, configuration-management]
---

Repo-tracked `.claude/settings.json` is symlink-installed via idempotent installer. Machine-local `.claude/settings.local.json` is gitignored and manually edited. Never symlink the whole `.claude` directory; stale permission entries accumulate and should be cleaned during config audits without losing active root settings.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
