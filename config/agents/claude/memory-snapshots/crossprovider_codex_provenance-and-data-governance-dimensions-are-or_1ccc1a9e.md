---
name: crossprovider codex provenance-and-data-governance-dimensions-are-or
description: Provenance and data-governance dimensions are orthogonal
metadata:
  type: reference
  source: codex
  bridged: 2026-07-19
  tags: [data-model, governance, schema-design, classification]
---

Source classification cannot be a single enumeration (e.g., 'canonical/duplicate/public/synthetic/private/licensed/derived'). These are logically independent: a source may be synthetic AND public AND licensed AND derived. Use separate fields: `canonical_source_id` (relationship), `release_status` (public/private/withheld), `license_class`, `source_origin` (synthetic/empirical/derived). Conflating them prevents deterministic eligibility decisions.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
