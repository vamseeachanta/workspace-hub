---
name: crossprovider codex digest-based-filtering-is-not-identity-validatio
description: Digest-based filtering is not identity validation
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [validation-gap, security-gate, test-coverage]
---

Selecting rows by `code_id in EXPECTED_DIGESTS` silently ignores unexpected rows outside that set. Identity validation must enumerate ALL expected rows (with explicit cardinality checks), and tests must prove that new/missing rows fail closed. Digest-only filtering allows wrong rows to pass if they have an expected digest value.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
