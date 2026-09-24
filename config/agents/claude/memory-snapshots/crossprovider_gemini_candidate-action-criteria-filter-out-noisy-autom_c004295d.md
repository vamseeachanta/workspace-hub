---
name: crossprovider gemini candidate-action-criteria-filter-out-noisy-autom
description: Candidate action criteria filter out noisy automation triggers
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [candidate-filtering, automation-threshold, signal-noise]
---

Skip candidate during Phase 5 if: name is empty/null, description is generic placeholder only, or occurrence count ≤ 2. Prevents spam WRK items from noise in tool-call data and repeated trial-and-error patterns that don't warrant automation.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
