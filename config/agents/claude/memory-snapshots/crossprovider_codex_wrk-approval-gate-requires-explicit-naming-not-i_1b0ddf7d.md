---
name: crossprovider codex wrk-approval-gate-requires-explicit-naming-not-i
description: WRK approval gate requires explicit naming, not intent
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [work-queue, approval-gates, contract-enforcement]
---

Work-queue contract blocks execution until user replies with literal 'Approve WRK-<id>' (e.g., 'Approve WRK-640'), not just plan approval or intent. This is the gating mechanism for all work orchestration; blocks are enforced at contract level across all provider CLIs.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
