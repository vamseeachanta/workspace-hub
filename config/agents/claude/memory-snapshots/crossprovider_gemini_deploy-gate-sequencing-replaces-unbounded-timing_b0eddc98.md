---
name: crossprovider gemini deploy-gate-sequencing-replaces-unbounded-timing
description: Deploy-gate sequencing replaces unbounded timing language
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [workflow, gate-policy, sequencing, specification]
---

Replace vague temporal commitments like 'same-day back-to-back merge' with concrete gate rules: 'Issue X shall not merge until Issue Y is approved-and-ready; both enter deploy queue at merge time.' Eliminates ambiguity about timing windows.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
