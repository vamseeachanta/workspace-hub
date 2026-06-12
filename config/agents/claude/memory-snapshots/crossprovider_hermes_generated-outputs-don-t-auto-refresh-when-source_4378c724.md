---
name: crossprovider hermes generated-outputs-don-t-auto-refresh-when-source
description: Generated outputs don't auto-refresh when source changes
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [artifacts, html, build-pipeline]
---

Edits to source text (e.g., removing placeholder language) leave generated HTML/PDF unchanged; tests pass because they read source, not output. Build/test flow requires explicit artifact-regeneration step, not lazy generation.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
