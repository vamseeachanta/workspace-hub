---
name: crossprovider codex csv-mixed-line-ending-preservation
description: CSV mixed line-ending preservation
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [csv, file-i-o, data-preservation]
---

When a CSV file has intentional mixed line endings (some rows LF, others CRLF), round-trip through csv.reader silently normalizes them all to LF, producing a phantom ~340-row diff even when only 1 row changed. Preserve by reading binary, recording each row's terminator, and replaying on write.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
