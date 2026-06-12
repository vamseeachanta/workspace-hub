---
name: crossprovider hermes post-processing-hiding-incomplete-source-state-i
description: Post-processing hiding incomplete source state in artifact tests
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [artifact-validation, post-processing, test-end-state, multi-format-testing]
---

When cleanup/transformation happens after core logic (e.g., hiding heatmaps via post-replace), source-level tests can pass while the final artifact remains incomplete. Tests must validate end-state artifacts after all post-processing, not just intermediate states. Similarly, tests must cover all required output formats (docx, PDF) not just primary ones (HTML/MD).

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
