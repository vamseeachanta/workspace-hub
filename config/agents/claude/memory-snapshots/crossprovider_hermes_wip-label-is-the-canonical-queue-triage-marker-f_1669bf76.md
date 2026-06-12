---
name: crossprovider hermes wip-label-is-the-canonical-queue-triage-marker-f
description: WIP label is the canonical queue triage marker for nightly batches
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [queue-triage, wip-label]
---

`gh issue list --label wip` is the source-of-truth for eligible nightly work, not session-signal files or side channels. Plan-approved + plan-review subsets of WIP determine execution vs. planning lanes.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
