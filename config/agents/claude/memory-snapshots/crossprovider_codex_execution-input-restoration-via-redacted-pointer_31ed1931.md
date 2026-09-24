---
name: crossprovider codex execution-input-restoration-via-redacted-pointer
description: Execution-input restoration via redacted pointers, not raw artifact copies
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [data-handling, governance, batch-processing, approval-workflow]
---

For approval-bound private inputs (e.g., Batch Pack 1/4), restore public-safe execution contracts using only hashes, checksums, schemas, and redacted path labels — never copy raw upstream files or private approval text into the public repo. Validation recipes and manifest metadata stay public; private locations remain external.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
