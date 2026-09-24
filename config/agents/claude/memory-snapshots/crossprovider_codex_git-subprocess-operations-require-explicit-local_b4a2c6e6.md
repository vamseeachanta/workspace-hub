---
name: crossprovider codex git-subprocess-operations-require-explicit-local
description: Git subprocess operations require explicit local-config disables
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git, subprocess-safety, config-isolation, local-includes]
---

Setting `GIT_CONFIG_NOSYSTEM` and `GIT_CONFIG_GLOBAL` environment variables is insufficient to isolate Git subprocess behavior. Local `.git/config` `include` directives and replacement refs still take effect. Fix: add `--no-replace-objects` flag, validate absence of `include.path` configuration, or use other explicit isolation mechanisms.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
