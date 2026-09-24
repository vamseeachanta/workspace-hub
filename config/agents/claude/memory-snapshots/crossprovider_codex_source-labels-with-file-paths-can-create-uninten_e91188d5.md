---
name: crossprovider codex source-labels-with-file-paths-can-create-uninten
description: Source labels with file paths can create unintended source-path maps in public artifacts
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [privacy-governance, data-abstraction, public-safety]
---

Exact source labels that include PDF filenames or relative paths (e.g., `mkt-a-dnv-rules:2018 DNVGL Ship Rules/docs/DNVGL-OS-E402.pdf`) risk turning GitHub comments/reports into documentation of the private source structure. Use opaque handles or digest-based identifiers in public comments; reserve exact labels for explicitly private artifacts.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
