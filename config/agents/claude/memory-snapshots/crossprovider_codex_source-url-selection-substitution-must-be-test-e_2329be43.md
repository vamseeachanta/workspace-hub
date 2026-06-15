---
name: crossprovider codex source-url-selection-substitution-must-be-test-e
description: Source-URL selection substitution must be test-encoded
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [testing, source-maps, intent-encoding]
---

When an implementation chooses different source URLs than parent-issue seeds, tests should encode both the canonical seed URL AND the substitution as expected values, not just assert whatever is currently in the file. This catches source-selection drift in CI.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
