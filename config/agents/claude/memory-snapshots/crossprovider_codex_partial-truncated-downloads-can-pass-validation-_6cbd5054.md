---
name: crossprovider codex partial-truncated-downloads-can-pass-validation-
description: Partial/truncated downloads can pass validation if checksums are computed on incomplete data
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [correctness, file-safety, network-edge-cases, testing]
---

Streaming download implementations that compute checksums on whatever bytes arrive, then atomically rename `.part` to final target without checking HTTP `Content-Length`, can produce 'valid' artifacts from truncated server responses. A short read will have a real checksum of incomplete bytes, defeating corruption detection. Compare received byte count to `Content-Length` header before final validation; use truncated payload test fixtures alongside error-response tests.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
