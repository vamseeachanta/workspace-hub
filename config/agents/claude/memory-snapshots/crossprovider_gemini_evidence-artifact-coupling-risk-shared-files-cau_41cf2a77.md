---
name: crossprovider gemini evidence-artifact-coupling-risk-shared-files-cau
description: Evidence artifact coupling risk: shared files cause premature stage completion
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [stage-orchestration, evidence-design, state-coupling]
---

When two stage-detection predicates depend on the same evidence file (e.g., gate-evidence-summary.json for both Stage 11 and 14), later stage jumps to 'done' as soon as earlier stage completes. Each stage needs unique or conditional detection artifacts.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
