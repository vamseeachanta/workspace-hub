---
name: crossprovider hermes nightly-batch-log-processing-requires-manual-fol
description: Nightly batch log processing requires manual follow-up
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [batch, automation, operations]
---

Launching 4 overnight lanes succeeds, but results live in `/logs/nightly-YYYY-MM-DD/*.log` and require manual inspection (grep completion, verify main landed). No auto-summarizer; each lane result is opaque until reviewed.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
