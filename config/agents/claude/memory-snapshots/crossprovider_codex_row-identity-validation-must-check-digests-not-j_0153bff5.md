---
name: crossprovider codex row-identity-validation-must-check-digests-not-j
description: Row identity validation must check digests, not just metadata categories
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [validation, row-identity, test-design]
---

Validating a row's `publisher == 'HSE'` and `status == 'public-agency-license-review-required'` is insufficient; two wrong rows with the same metadata would still pass. Tests should assert exact expected row digests/IDs from manifest. A tranche must enumerate the intended rows by content hash or live identifier, not just count and category.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
