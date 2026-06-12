---
name: crossprovider hermes delegate-task-defaults-to-claude-gemini-requires
description: delegate_task defaults to Claude; Gemini requires explicit provider routing
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [hermes, gemini, agent-dispatch]
---

Hermes delegate_task doesn't support per-task model selection—always routes to Claude Sonnet 4.6. To use Gemini, must invoke directly (not via delegate_task). Gemini needs copilot provider + --yolo flag. Impact: overnight research batches requiring Gemini must run as direct Hermes commands, not subagents.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
