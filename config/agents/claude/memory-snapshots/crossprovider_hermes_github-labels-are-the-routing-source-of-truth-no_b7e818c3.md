---
name: crossprovider hermes github-labels-are-the-routing-source-of-truth-no
description: GitHub labels are the routing source-of-truth, not separate queue files
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [github-workflow, agent-routing, automation]
---

Use `agent:gemini`, `agent:claude`, `agent:codex` labels directly on GitHub issues for deterministic agent routing. Query with `gh issue list --label "agent:gemini,priority:high"`. Labels live on the issue itself and never drift; separate markdown queue files become stale.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
