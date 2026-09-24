---
name: crossprovider codex evidence-types-have-different-acceptance-tiers-n
description: Evidence types have different acceptance tiers; not all sources qualify as active conversion factors
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [evidence-acceptance, data-quality, conversion-factors]
---

During source verification, discovery-test API values, range evidence, and secondary/industry sources can be stored in a registry as evidence-only, but only representative peer-reviewed measurements qualify as accepted conversion factors that drive normalization. Policy gap: a field with only discovery-test evidence should not silently use that factor; instead, flag it as defaulted or missing for operator review.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
