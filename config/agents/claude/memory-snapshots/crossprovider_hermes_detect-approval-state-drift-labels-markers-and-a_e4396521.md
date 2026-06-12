---
name: crossprovider hermes detect-approval-state-drift-labels-markers-and-a
description: Detect approval state drift: labels, markers, and artifacts must align
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [approval, state-drift, labels, markers]
---

Plan approval drifts when GitHub labels claim status:plan-approved but review artifacts are missing/malformed, or marker files diverge from label state. Monitor this trio: GitHub labels, local marker files, artifact presence. Mismatch = stale approval state and real credibility risk.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
