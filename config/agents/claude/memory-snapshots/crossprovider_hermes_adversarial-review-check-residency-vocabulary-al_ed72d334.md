---
name: crossprovider hermes adversarial-review-check-residency-vocabulary-al
description: Adversarial review: check residency vocabulary alignment across layers
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [adversarial-review, cross-layer-contracts, vocabulary-gap]
---

Execution manifests with freeform input_residency/output_residency fields (e.g. 'owner repo checkout') do not align with report layer's closed enum (public_llm_wiki, domain_private_corpus, etc.). Fixtures testing on placeholder values won't surface actual gate gaps; both sides must use identical closed vocabulary list.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
