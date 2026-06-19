---
name: crossprovider codex input-field-safety-requires-allowlist-of-safe-fi
description: Input field safety requires allowlist of safe fields, not just output deny-tests
metadata:
  type: reference
  source: codex
  bridged: 2026-06-18
  tags: [input-validation, field-governance, safe-fields-only]
---

Output deny-list tests for 'no /mnt/' or 'no password=' do not catch unsafe input fields like `indexlike_examples` that contain relative paths and filenames. Define the safe input-field set explicitly (e.g., counts, digests, labels only) and exclude unsafe source fields before processing.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
