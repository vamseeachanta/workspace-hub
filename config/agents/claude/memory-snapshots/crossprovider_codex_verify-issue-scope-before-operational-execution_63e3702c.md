---
name: crossprovider codex verify-issue-scope-before-operational-execution
description: Verify issue scope before operational execution
metadata:
  type: reference
  source: codex
  bridged: 2026-07-07
  tags: [issue-driven-workflow, scope-clarity, authorization]
---

Before running existing code against production (e.g., live refresh, scheduler job), check for an approved issue and confirm whether the work is validation/operational (run merged code) vs new implementation (change code). This prevents scope creep and ensures authorization.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
