---
name: crossprovider codex git-status-slowness-in-large-monorepos-use-bound
description: Git status slowness in large monorepos; use bounded queries
metadata:
  type: reference
  source: codex
  bridged: 2026-06-18
  tags: [git, performance, monorepo]
---

In large repos (625M+), `git status --short` and `git diff --stat` hang or timeout. Use `git diff --cached`, `git ls-files`, or path-scoped queries; set tight timeouts; cancel slow probes rather than waiting. Affects CI, parallel-session detection, and code review metadata.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
