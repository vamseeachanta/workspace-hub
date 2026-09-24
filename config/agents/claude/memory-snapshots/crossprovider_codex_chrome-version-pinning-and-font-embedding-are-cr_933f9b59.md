---
name: crossprovider codex chrome-version-pinning-and-font-embedding-are-cr
description: Chrome version pinning and font embedding are critical for PDF reproducibility
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [plan-review, codex-pattern, pdf-rendering, reproducibility]
---

Chrome headless versions differ (100 vs 147) in rendering output. Plans must assert Chrome version and fail hard on mismatch, not warn-only. Fonts must be embedded in the PDF or vendored locally (WOFF2 files with license), not referenced via fonts.googleapis.com network call. Missing version pin or network font deps = MAJOR.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
