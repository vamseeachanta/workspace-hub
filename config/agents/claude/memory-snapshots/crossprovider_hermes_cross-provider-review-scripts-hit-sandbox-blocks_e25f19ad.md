---
name: crossprovider hermes cross-provider-review-scripts-hit-sandbox-blocks
description: Cross-provider review scripts hit sandbox blocks
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [review, sandbox, cross-provider]
---

Codex can't read local files from sandbox, Gemini has visibility gaps on sparse-checkout overlays. `cross-review.sh` fails silently; fallback is single-author self-review with explicit provenance. For multi-provider, push to GitHub first, then review live GH artifacts.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
