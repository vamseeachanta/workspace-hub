---
name: crossprovider codex public-token-contracts-need-explicit-field-level
description: Public token contracts need explicit field-level privacy boundaries
metadata:
  type: reference
  source: codex
  bridged: 2026-07-04
  tags: [contracts, token-privacy, field-level-spec]
---

Public outputs must specify which fields are private-only (`source_id`, `source_sha256`) vs public with grammar rules (`public_source_token`). Field naming alone is insufficient; the contract must define placement and format.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
