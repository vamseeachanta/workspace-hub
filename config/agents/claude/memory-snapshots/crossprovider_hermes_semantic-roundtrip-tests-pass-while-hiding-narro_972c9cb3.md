---
name: crossprovider hermes semantic-roundtrip-tests-pass-while-hiding-narro
description: Semantic roundtrip tests pass while hiding narrow field mappings
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [testing, semantic-validation, roundtrip]
---

Test suites can roundtrip successfully but miss gaps in specific field transformations (e.g., analysis_type ↔ solve_type, qtf_min/max parsing). Solver defaults/fallbacks mask missing overrides. Check generated native outputs and reverse-parser coverage separately. (#2455–#2457)

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
