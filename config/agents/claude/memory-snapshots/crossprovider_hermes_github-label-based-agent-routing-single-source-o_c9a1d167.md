---
name: crossprovider hermes github-label-based-agent-routing-single-source-o
description: GitHub label-based agent routing: single source of truth
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [GitHub, routing, labels, automation]
---

`agent:gemini`, `agent:claude`, `agent:codex` labels on issues make routing deterministic and visible in UI. Generate work queue via `gh issue list --label "agent:X"` instead of maintaining separate files. Batch-label 175+ issues via API; reassign anytime. No drift between queue and GitHub.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
