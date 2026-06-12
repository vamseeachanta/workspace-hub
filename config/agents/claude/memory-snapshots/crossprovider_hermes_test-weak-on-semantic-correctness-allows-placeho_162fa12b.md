---
name: crossprovider hermes test-weak-on-semantic-correctness-allows-placeho
description: Test-weak on semantic correctness allows placeholders to slip through
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [testing, tdd, test-gaps]
---

Tests can pass while hardcoded constants like 'OCIMF-inspired' and placeholder text remain in actual output. Structure-only validation misses semantic correctness gaps. Verify output against plan artifacts explicitly, not just test existence.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
