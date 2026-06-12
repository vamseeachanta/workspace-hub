---
name: crossprovider hermes checksum-validation-requires-semantic-verificati
description: Checksum validation requires semantic verification beyond regex
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [schema, validation, checksums, semantic]
---

Schema validation using regex pattern matching (e.g., `sha256:<64 hex>`) catches syntax errors but allows fabricated digests. Add semantic verification that rejects checksums not matching actual file content (compute SHA-256 and compare). Pattern + semantic verification together prevent both syntax violations and forged digests.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
