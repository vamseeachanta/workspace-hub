---
name: crossprovider hermes large-diffs-strain-cross-provider-review-coordin
description: Large diffs strain cross-provider review coordination
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [cross-provider, review, scaling]
---

80K+ character diffs cause input-size concerns when delegating to Codex/Gemini via stdin. Chunk by file or split reviews across multiple agents per file when diff exceeds ~50K characters.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
