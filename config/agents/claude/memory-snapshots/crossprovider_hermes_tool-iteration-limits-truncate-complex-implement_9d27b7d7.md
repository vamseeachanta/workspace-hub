---
name: crossprovider hermes tool-iteration-limits-truncate-complex-implement
description: Tool iteration limits truncate complex implementation tasks
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [hermes-constraints, implementation, tool-limits]
---

Multiple Hermes sessions on #2760 and #2766 hit "maximum tool-calling iterations allowed" mid-task, forcing premature completion summaries. Complex multi-file changes (TDD implementation, artifact generation, validation) often exceed iteration budget before finishing.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
