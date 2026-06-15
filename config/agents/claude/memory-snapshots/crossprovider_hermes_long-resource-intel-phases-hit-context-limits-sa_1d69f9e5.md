---
name: crossprovider hermes long-resource-intel-phases-hit-context-limits-sa
description: Long resource-intel phases hit context limits; save checkpoints to disk
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [hermes, resource-gathering, context-management]
---

When resource-intelligence gathering spans 4+ compressed Hermes sessions (each with 11+ messages removed), the task loop isn't advancing—context expires before findings land. For large-scope intel (multi-file reads, repo structure surveys, mkt-a outputs), save intermediate findings to a persistent artifact file before context compaction. This unblocks the next session to resume from checkpoints rather than restart.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
