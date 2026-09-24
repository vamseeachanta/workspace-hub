---
name: crossprovider codex aggregate-only-reports-prevent-manual-review-lea
description: Aggregate-only reports prevent manual-review leakage
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [privacy, artifact-design, manual-review]
---

Routing/disposition reports must use opaque IDs and enum outcomes only, never filenames, source paths, page numbers, or raw bodies. This applies even to intermediate artifacts that may be manually reviewed or shared. Use hashes/extensions only.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
