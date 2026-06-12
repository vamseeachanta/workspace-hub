---
name: crossprovider hermes output-level-residency-bypasses-manifest-level-p
description: Output-level residency bypasses manifest-level promotion gates
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [schema-validation, promotion-gates, data-boundaries]
---

Execution manifests allow individual outputs to specify output_residency: public_llm_wiki while manifest-level is domain_private_corpus; schema doesn't enforce residency inheritance, causing promotion-gate checks tied to manifest residency to be bypassed. Outputs should inherit or match manifest residency to enforce gates uniformly.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
