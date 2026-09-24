---
name: crossprovider gemini checksum-scope-guard-verification-pattern-for-fi
description: Checksum + scope-guard verification pattern for file migrations
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [migration, verification, data-integrity]
---

Use SHA-256 checksums with normalized path diff, inventory counts for completeness, regex-based scope guards to prevent scope creep, and pointer-file validation. This pattern prevents silent data loss and unintended changes during large-scale file reorganizations.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
