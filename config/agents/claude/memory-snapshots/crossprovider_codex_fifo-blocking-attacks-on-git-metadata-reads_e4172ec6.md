---
name: crossprovider codex fifo-blocking-attacks-on-git-metadata-reads
description: FIFO blocking attacks on Git metadata reads
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git-security, subprocess-safety, timeout-handling]
---

Git subprocesses reading from mutable `.git` entries (like `.git/HEAD` or `refs/heads/main`) can block indefinitely if those entries are replaced with FIFO files. Require finite timeouts (5–10 seconds) with fail-closed translation, or descriptor-attest entries before subprocess invocation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
