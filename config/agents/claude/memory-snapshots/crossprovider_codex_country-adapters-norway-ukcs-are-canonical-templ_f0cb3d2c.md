---
name: crossprovider codex country-adapters-norway-ukcs-are-canonical-templ
description: Country adapters: Norway/UKCS are canonical templates
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [architecture-patterns, adapters, countries]
---

New country chains should replicate the Norway and UKCS reference_chain.py and field_concept.py structure rather than innovating. Both use ProductionQuery -> adapter.fetch(STANDARD_COLUMNS) -> to_fdas_production contract path; mirroring ensures FDAS and cross-country consistency.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
