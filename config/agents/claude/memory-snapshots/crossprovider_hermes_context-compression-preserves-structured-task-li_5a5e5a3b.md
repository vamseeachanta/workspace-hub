---
name: crossprovider hermes context-compression-preserves-structured-task-li
description: Context compression preserves structured task lists
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [system-behavior, context-management, hermes]
---

Hermes maintains task lists across context compression boundaries (e.g., `[>] resource-intel. Gather...` checklist survives multiple truncations). Session continuity relies on this state preservation, not chat context.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
