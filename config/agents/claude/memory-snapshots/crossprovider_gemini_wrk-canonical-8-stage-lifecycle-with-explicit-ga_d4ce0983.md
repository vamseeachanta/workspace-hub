---
name: crossprovider gemini wrk-canonical-8-stage-lifecycle-with-explicit-ga
description: WRK canonical 8-stage lifecycle with explicit gates
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [workflow, work-queue, governance]
---

Work items flow through: Capture → Resource Intelligence → Triage → Plan → Claim → Execute → Close → Archive. Each stage has specific deliverables and gate criteria. User HTML review is mandatory before plan approval, and implementation review must pass before closure.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
