---
name: crossprovider hermes subagent-model-routing-unavailable
description: Subagent model routing unavailable
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [limitation, agents, gemini, architecture]
---

delegate_task does not support per-task model selection; all subagents run on Claude Sonnet regardless of intent. Gemini-specific tasks cannot be delegated. Workaround: execute Gemini-bound work directly in main session.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
