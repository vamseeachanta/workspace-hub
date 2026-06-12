---
name: crossprovider hermes label-based-work-queue-prevents-drift-from-exter
description: Label-based work queue prevents drift from external markdown
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [work-queue, github-automation, routing]
---

GitHub labels (`agent:gemini`, `agent:claude`, `agent:codex`) as source-of-truth for work routing stay in sync better than external markdown queue file. Labels are queryable, visible in UI, and live on the issue itself — markdown diverges quickly. Refresh script queries labels not file.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
