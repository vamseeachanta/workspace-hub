---
name: crossprovider codex git-contention-under-20-concurrent-processes-cau
description: Git contention under 20+ concurrent processes causes indefinite hangs
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [parallel-contention, git-lock, timeout-pattern]
---

Parallel session load on shared workspace-hub causes `git status`, `git ls-files`, and `uv` initialization to hang for 15s–minutes without output. Mitigation: use timeouts, switch to narrower non-recursive commands, avoid broad status/diff in high-concurrency windows.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
