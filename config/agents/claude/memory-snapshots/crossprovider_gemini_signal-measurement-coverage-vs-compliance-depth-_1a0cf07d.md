---
name: crossprovider gemini signal-measurement-coverage-vs-compliance-depth-
description: Signal measurement coverage vs. compliance depth are distinct metrics
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [governance-metrics, signal-tracking, workflow-gates]
---

For workflow governance, distinguish between **measurement coverage** (all contract signals are present in the dataset at least once) and **compliance depth** (how frequently each signal fires). A gate can report "23/23 signals measured" (coverage) while compliance depth still varies by stage. Only explicit signals logged by scripts/gates count; inferred signals are diagnostic only.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
