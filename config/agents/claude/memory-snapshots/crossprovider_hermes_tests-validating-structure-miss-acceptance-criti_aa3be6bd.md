---
name: crossprovider hermes tests-validating-structure-miss-acceptance-criti
description: Tests validating structure miss acceptance-critical mappings
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [testing, tdd, acceptance-criteria]
---

Tests passing on field presence don't catch missing mappings that acceptance criteria require. E.g., #2508: tests verified YAML shape and report strings but not per-role tools/evidence/source-limitations mappings. Test the acceptance criteria themselves, not just data structure.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
