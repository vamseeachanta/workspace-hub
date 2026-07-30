---
name: crossprovider codex git-subprocess-timeout-boundary-prevents-fifo-ha
description: Git subprocess timeout boundary prevents FIFO hangs
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [git, subprocess, security, denial-of-service]
---

Git I/O on HEAD/refs can hang indefinitely on FIFO/corrupt entries → require finite bounded timeouts (e.g., 5 seconds) with fail-closed error translation. Add adversarial FIFO tests for both `.git/HEAD` and `refs/heads/main`. Text-only validation (symbolic-ref match) is insufficient.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
