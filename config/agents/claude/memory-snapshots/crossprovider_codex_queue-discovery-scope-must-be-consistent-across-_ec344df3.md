---
name: crossprovider codex queue-discovery-scope-must-be-consistent-across-
description: Queue discovery scope must be consistent across all tools
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [queue-system, consistency, architecture]
---

When multiple tools query the same queue system, inconsistent discovery scope (e.g., some reading `pending/` only, others reading `pending/ + done/ + archived/`) causes state rollups to diverge. Centralize queue lookup in a shared helper or document a strict scope contract.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
