---
name: crossprovider codex multi-step-github-mutations-need-transaction-saf
description: Multi-step GitHub mutations need transaction safety and idempotence
metadata:
  type: reference
  source: codex
  bridged: 2026-07-18
  tags: [github-api, transactions, resilience, scripting]
---

`gh issue create` followed by downstream jq/redirection/file operations can orphan GitHub issues if the session fails mid-sequence. If step N+1 fails after issue creation but before persisting the issue number, rerunning the plan recreates the child. Store returned resource IDs in committed state before proceeding; define explicit rollback steps for partial failures; avoid `|| true` on essential operations.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
