---
name: crossprovider gemini stop-hook-performance-constraint-5-seconds-for-s
description: Stop hook performance constraint: <5 seconds for stage-gate compatibility
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [performance-constraint, hook-optimization, stage-gates]
---

Tidy fires at every stage-gate Stop hook (stages 1–20). Must complete <5s to avoid cumulative UX degradation across 20 stages.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
