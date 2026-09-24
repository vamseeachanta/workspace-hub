---
name: crossprovider codex unsafe-pkill-f-pattern-in-agent-automation
description: Unsafe pkill -f pattern in agent automation
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [agent-safety, shell-automation, process-management]
---

The pattern `pkill -f 'pattern|...'` can match the invoking shell/process chain itself, causing self-inflicted session failure. In agent sessions that automate shells, this is a failure mode to avoid. Safer: use specific process identifiers or avoid pkill for terminating related work.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
