---
name: crossprovider codex source-metadata-needs-independent-dimensions-not
description: Source metadata needs independent dimensions, not mutually-exclusive enum
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [schema-design, data-governance, classification-design]
---

License status, canonical relationship, derivation status, and confidentiality are independent governance dimensions. Over-eager single-enum design (e.g., canonical/duplicate/public/synthetic/private/licensed/derived) blocks downstream eligibility logic. Separate fields: source_class, canonical_source_id, license_class, release_status.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
