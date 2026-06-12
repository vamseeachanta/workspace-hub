---
name: crossprovider hermes git-subprocess-timeout-in-local-checks
description: Git subprocess timeout in local checks
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [subprocess-safety, git-quirks, operations]
---

Read-only git operations (git status, git rev-list) without timeout can hang indefinitely on pathological git configs (fsmonitor hooks, slow filters). New local checkers should match existing timeout patterns (timeout=60s in parallel code) to avoid blocking the readiness pipeline.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
