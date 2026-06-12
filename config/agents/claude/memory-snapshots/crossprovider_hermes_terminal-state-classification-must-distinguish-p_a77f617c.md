---
name: crossprovider hermes terminal-state-classification-must-distinguish-p
description: Terminal state classification must distinguish partial completion
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [terminal-classification, evidence-based, monitoring]
---

Always distinguish `succeeded` vs `blocked_partial` vs `failed` vs `timed out` vs `canceled`; do not conflate partial completions into success. Evidence is the arbiter: zero exit code + closed issues + clean branch = `succeeded`; some issues closed + documented blockers = `blocked_partial`.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
