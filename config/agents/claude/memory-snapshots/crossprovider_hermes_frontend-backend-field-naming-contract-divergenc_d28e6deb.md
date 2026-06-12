---
name: crossprovider hermes frontend-backend-field-naming-contract-divergenc
description: Frontend-backend field naming contract divergence causes silent integration bugs
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [integration, contract-first, frontend-backend-alignment]
---

HTML/JS code references field names that either don't exist in the backend data structure or are named differently; neither layer validates the contract. Requires explicit schema, interface, or shared type definition before implementation to catch mismatches early, not at render time.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
