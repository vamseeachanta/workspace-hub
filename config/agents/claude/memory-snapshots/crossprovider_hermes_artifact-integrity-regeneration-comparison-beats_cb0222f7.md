---
name: crossprovider hermes artifact-integrity-regeneration-comparison-beats
description: Artifact integrity: regeneration+comparison beats freshness checks alone
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [artifact-validation, tamper-detection]
---

In #77 validator, fail-closed auditing required checking CSV presence/matching and comparing regenerated graph content against checked-in artifacts to detect tampering. Counting nodes/edges and checking corpus digest are insufficient—an attacker can keep counts/digest constant while modifying content. For public/published artifacts, regenerate and compare, or fail closed.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
