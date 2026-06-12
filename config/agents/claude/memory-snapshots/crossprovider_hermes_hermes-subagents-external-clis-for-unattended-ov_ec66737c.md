---
name: crossprovider hermes hermes-subagents-external-clis-for-unattended-ov
description: Hermes subagents > external CLIs for unattended overnight work
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [hermes, overnight-batch, orchestration, auth]
---

Claude Code, Codex, and Gemini CLIs all fail unpredictably in unattended mode: Claude OAuth expires mid-task, Codex has config issues, Gemini sandbox blocks headless execution. Use Hermes `delegate_task` with `delegation.model=sonnet` instead—it runs via API, no auth expiry, and completes autonomously.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
