---
name: crossprovider codex digest-set-validation-cannot-replace-row-set-val
description: Digest-set validation cannot replace row-set validation
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [validation, data-integrity, testing]
---

Comparing sets of digests (e.g., expected vs actual digest hashes) does not catch duplicate row IDs or wrong row IDs paired with expected digests. Need pair-based validation: `(code_id, digest)` tuples or explicit cardinality checks per row ID.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
