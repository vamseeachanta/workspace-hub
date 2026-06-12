---
name: crossprovider hermes adversarial-review-catches-oracle-leakage-in-eva
description: Adversarial review catches oracle leakage in evaluation scripts
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [adversarial-review, validation, oracle-leakage, evaluation]
---

Gold answer fields (required_citations, required_facts) can inadvertently boost model rankings if not strictly isolated at evaluation boundaries. Probe with nonsensical queries + oracle fields populated to verify ranking/synthesis follows only retrieved contexts, not gold answers.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
