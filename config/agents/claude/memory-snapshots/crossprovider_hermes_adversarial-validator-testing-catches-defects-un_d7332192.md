---
name: crossprovider hermes adversarial-validator-testing-catches-defects-un
description: Adversarial validator testing catches defects unit tests miss
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [validation, testing, adversarial, schema, llm-wiki]
---

Unit test passes do not guarantee validator completeness. Adversarial tampering—inject false CSV rows, create self-edges, plant unresolved targets, add stale artifacts—reveals actual gaps. Fixture schema parity (row count vs. content parity) and edge cases (wikilink/markdown parsing collisions, anchored targets) require explicit adversarial test coverage to be comprehensive.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
