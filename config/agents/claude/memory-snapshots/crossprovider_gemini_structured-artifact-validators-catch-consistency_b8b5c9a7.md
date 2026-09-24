---
name: crossprovider gemini structured-artifact-validators-catch-consistency
description: Structured artifact validators catch consistency and completeness errors
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [validation, gates, structured-artifacts, quality-checks]
---

Complex artifact stages (e.g., Resource Intelligence packs) benefit from mechanical validators checking: required files present, heading structure correct, source references attached, user decisions non-contradictory (e.g., fail if P1 gaps exist but user chose `continue_to_planning`), legal-scan reference present, indexing reference present.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
