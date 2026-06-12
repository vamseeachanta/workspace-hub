---
name: crossprovider hermes github-labels-are-the-source-of-truth-for-agent-
description: GitHub labels are the source-of-truth for agent routing, not separate config
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [agent-routing, github-workflow, no-drift-patterns]
---

Bake agent:gemini/agent:claude/agent:codex labels directly onto GitHub issues instead of maintaining a separate queue file that can drift. The label IS the routing instruction. Query with `gh issue list --label "agent:gemini,priority:high"` to fetch the queue dynamically. Reassign anytime via `gh issue edit`.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
