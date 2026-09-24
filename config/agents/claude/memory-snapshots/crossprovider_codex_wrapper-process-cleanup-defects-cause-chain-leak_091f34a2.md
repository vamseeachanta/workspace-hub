---
name: crossprovider codex wrapper-process-cleanup-defects-cause-chain-leak
description: Wrapper process cleanup defects cause chain leaks
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [process-management, cleanup, timeouts, reliability]
---

Timeout/force-end operations on cross-review wrappers can leak process chains, particularly at Gemini submission path or with 60-second wrapper timeout. Hanging processes require explicit force-kill rather than graceful shutdown.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
