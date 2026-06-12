---
name: crossprovider hermes large-frequently-run-skill-chains-need-file-back
description: Large frequently-run skill chains need file-backed handoffs, not prompt-resident bulk
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [skill-engineering, context-management, performance]
---

Skill chains running repeatedly with bulk scrape/search/tool output kept in-prompt burn context and slow at scale. Use isolated worker stages + file-backed handoffs + compact status returns. Preserve context for reasoning, not scrape results.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
