---
name: crossprovider hermes native-claude-does-not-flow-through-hermes-agent
description: Native Claude does not flow through Hermes Agent runtime
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [provider-ecosystem, hermes, claude, architecture]
---

Native Claude and Hermes are parallel ecosystems. Claude writes to `.claude/state/sessions/session_YYYYMMDD.jsonl` and `logs/orchestrator/claude/session_YYYYMMDD.jsonl` via hooks; Hermes maintains its own state. They do not cross-invoke. For cross-provider memory consolidation, both must be imported separately into a canonical store (e.g., via `distill-provider-sessions.py`).

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
