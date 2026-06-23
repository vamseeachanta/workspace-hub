---
name: crossprovider codex byte-for-byte-reproducibility-check-for-generate
description: Byte-for-byte reproducibility check for generated reports catches invocation drift
metadata:
  type: reference
  source: codex
  bridged: 2026-06-22
  tags: [reproducibility, idempotency-testing, format-handling]
---

Verify regenerated HTML/JSON from sorted data matches original; idempotency tests must assert first-run/second-run equality. Format reordering (JSON key sort on readback) can create false negatives if only text comparison is used. Serialize and compare exact bytes.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
