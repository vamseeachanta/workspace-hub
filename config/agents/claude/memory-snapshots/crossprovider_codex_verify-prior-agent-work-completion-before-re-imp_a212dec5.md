---
name: crossprovider codex verify-prior-agent-work-completion-before-re-imp
description: Verify prior agent work completion before re-implementing
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [multi-agent-coordination, workflow-efficiency, git-state]
---

When resuming issues where other agents (Hermes, Codex) already landed commits, verify the current HEAD state and distinguish between 'already completed' vs 'blocked by missing data' before re-implementing. Checking pushed artifacts first saves rework.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
