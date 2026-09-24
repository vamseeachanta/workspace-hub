---
name: crossprovider codex fail-closed-architecture-for-source-gaps
description: Fail-closed architecture for source gaps
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [data-quality, fail-closed, audit-trail]
---

Missing conversion factors are explicitly marked as `accepted_for_conversion=false` with `bbl_per_tonne=null`, raising `CoresDensityCoverageError` in strict audit mode. Permissive mode can optionally default only when explicitly enabled, with audit trail recording which fields were defaulted. This prevents silent fallbacks to weak sources.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
