---
name: crossprovider codex access-control-boundaries-require-explicit-testa
description: Access-control boundaries require explicit testability, not output-only checks
metadata:
  type: reference
  source: codex
  bridged: 2026-06-21
  tags: [testing, security, governance]
---

Leak detection via output inspection cannot prove source-body was never accessed (could be paraphrased). For legal/compliance gates on raw-source access, tests must explicitly verify no file-open or resolver-access attempts occur, not just that final output is clean.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
