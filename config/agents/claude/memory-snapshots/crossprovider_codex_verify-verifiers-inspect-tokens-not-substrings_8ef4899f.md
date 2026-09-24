---
name: crossprovider codex verify-verifiers-inspect-tokens-not-substrings
description: Verify verifiers inspect tokens, not substrings
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [implementation-lesson, verification]
---

Verifier tools must inspect command tokens rather than raw substrings to avoid false positives. Example: a path-utils verifier treating `src/assethold/...` as matching an old `src/` target pattern by substring.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
