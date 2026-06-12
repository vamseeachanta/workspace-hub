---
name: crossprovider codex spec-conversion-acceptance-criteria-often-lack-s
description: Spec-conversion acceptance criteria often lack semantic and fidelity coverage
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [acceptance-criteria, domain-conversion, plan-review]
---

Ballymore-to-OrcaFlex plan reviews found recurring gap: acceptance criteria assert structure (counts, keys, nesting) but not semantics (values derived from source, not hardcoded) or fidelity (distinct input variants produce distinct outputs, or reuse explicitly justified). Count-only assertions ("27 rows exist") let converters emit placeholder values that pass tests. Future spec-conversion plan reviews should verify acceptance covers all three dimensions.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
