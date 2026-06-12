---
name: crossprovider hermes async-batch-completion-requires-output-exists-an
description: Async batch completion requires output-exists AND PIDs-dead
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [parallel-monitoring, process-completion, polling-pattern]
---

Monitoring 10 parallel Claude planning runs required checking both conditions: all 10 dossier files present AND no Claude processes remaining alive. Output-only is insufficient; a process may restart. Pattern: dual-condition polling for async workflows.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
