---
name: crossprovider gemini version-string-matching-should-use-substring-or-
description: Version string matching should use substring or env var, not exact equality
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [version-matching, portability, brittle-assertions]
---

Exact-match rules like `foamVersion == OpenFOAM-v2312` fail across vendor distributions (ESI outputs `2312`, `2312 (ESI)`, or via `$WM_PROJECT_VERSION`). Use substring match on stdout or inspect environment variable for portability.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
