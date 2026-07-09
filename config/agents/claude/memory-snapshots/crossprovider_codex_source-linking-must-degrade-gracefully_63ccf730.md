---
name: crossprovider codex source-linking-must-degrade-gracefully
description: Source-linking must degrade gracefully
metadata:
  type: reference
  source: codex
  bridged: 2026-07-03
  tags: [html, linking, provenance]
---

HTML links to source files become false evidence if source and output roots diverge. If paths are not relative to output, render as escaped text provenance statement, not href, to avoid false clickability.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
