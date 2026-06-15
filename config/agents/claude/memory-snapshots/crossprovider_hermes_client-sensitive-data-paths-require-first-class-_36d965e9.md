---
name: crossprovider hermes client-sensitive-data-paths-require-first-class-
description: Client-sensitive data paths require first-class schema, not prose intent
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [raw-data-boundaries, client-sensitivity, schema-design]
---

When raw-data boundaries reference client-specific paths (e.g., `client-c/<org>/`), declare sensitivity classification as a required schema field (approval-gated, client-sensitive, etc.), not just narrative approval-gate mentions.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
