---
name: crossprovider hermes continuous-approval-buffer-prevents-overnight-im
description: Continuous approval buffer prevents overnight implementation starvation
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [ai-orchestration, workflow, overnight-work, issue-pipeline]
---

Maintain 5–10 issues in `status:plan-approved` + local marker so overnight implementation never blocks on waiting for morning review/approval. Combined with 5–10 more in planning queue, this creates a continuous day/night cycle: day shift does intake/planning/approval, night shift executes approved work.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
