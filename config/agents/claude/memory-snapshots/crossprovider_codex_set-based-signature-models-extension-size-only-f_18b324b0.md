---
name: crossprovider codex set-based-signature-models-extension-size-only-f
description: Set-based signature models (extension+size only) falsely collapse distinct files as duplicates
metadata:
  type: reference
  source: codex
  bridged: 2026-06-18
  tags: [duplicate-detection, signature-model, false-positives]
---

Using only `extension:byte_size` as a file signature and storing in a Python `set()` loses multiplicity. Five distinct 100KB PDFs become one signature; false-positive duplicate claims follow. Use `Counter` / multiset model or add content-hash tier for deletion-risk decisions.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
