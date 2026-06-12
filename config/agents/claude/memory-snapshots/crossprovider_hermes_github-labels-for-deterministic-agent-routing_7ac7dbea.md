---
name: crossprovider hermes github-labels-for-deterministic-agent-routing
description: GitHub labels for deterministic agent routing
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [agent-routing, github-labels, multi-agent-dispatch]
---

Use `agent:gemini/claude/codex/any` labels directly on issues as the routing instruction. The work queue is auto-generated via `gh issue list --label` queries, preventing drift. Labels are the source of truth and queryable in GitHub UI; reassignment is trivial via `gh issue edit`.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
