---
name: crossprovider codex lane-classification-requires-evidence-fusion-not
description: Lane classification requires evidence fusion, not labels alone
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [work-queue, issue-classification, evidence-fusion]
---

Issue queues classified by execution-readiness lanes (A/B/C for approval/execution/planning) must combine evidence from GitHub labels, canonical plan files, review verdicts, approval markers, and freshness signals. Label-only classification is unsafe and can leak incomplete work into execution queues.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
