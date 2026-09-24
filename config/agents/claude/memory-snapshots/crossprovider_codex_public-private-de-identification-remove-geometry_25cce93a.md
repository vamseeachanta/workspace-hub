---
name: crossprovider codex public-private-de-identification-remove-geometry
description: Public/private de-identification: remove geometry, values, client names; preserve interfaces
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [privacy, de-identification, public-repos]
---

Reusable code modules destined for public repos must have client/job-specific defaults, geometry, values, and identifiers removed. Generic contract surfaces (coupling interfaces, input/output shapes, synthetic test fixtures) are reusable and de-identified; only these survive promotion to public.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
