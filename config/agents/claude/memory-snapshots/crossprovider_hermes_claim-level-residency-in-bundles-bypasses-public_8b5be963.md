---
name: crossprovider hermes claim-level-residency-in-bundles-bypasses-public
description: Claim-level residency in bundles bypasses public-gate enforcement
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [report-layer, data-residency, fail-closed]
---

Report evidence bundles allow individual claims output_residency: domain_private_corpus while bundle-level is public_llm_wiki; schema doesn't bind them, allowing private claims in public reports without full promotion gates. Bundle-level public classification should require claim-residency matching or explicit rejection.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
