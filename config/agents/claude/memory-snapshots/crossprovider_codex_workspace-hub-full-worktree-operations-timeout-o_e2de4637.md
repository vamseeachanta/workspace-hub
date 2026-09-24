---
name: crossprovider codex workspace-hub-full-worktree-operations-timeout-o
description: Workspace-hub full-worktree operations timeout on 10s budgets
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [performance, workspace-hub, timeout]
---

`git status`, work-queue scans, and similar operations that touch all checked-out files exceed 10-second timeouts on ace-linux-1. Tests, validators, and monitoring scripts should use narrower checks or longer timeouts. Affects queue validation, index generation, and usage auditing.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
