---
name: crossprovider codex uv-availability-and-health-checks-before-python-
description: uv availability and health checks before Python invocation
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [tooling, gates, reliability, multi-provider]
---

Gate scripts and cross-provider workflows must check uv availability (command -v uv) and functional health (uv run --no-project python -c "print(1)") before invoking Python. Assume uv may be missing, installed but broken, or in an inconsistent state on remote hosts. Validate early to fail fast.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
