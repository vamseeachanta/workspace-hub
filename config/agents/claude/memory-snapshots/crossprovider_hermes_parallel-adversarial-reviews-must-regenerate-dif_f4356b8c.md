---
name: crossprovider hermes parallel-adversarial-reviews-must-regenerate-dif
description: Parallel adversarial reviews must regenerate diff per provider to avoid stale input
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [cross-provider-review, artifact-staleness, parallel-agents]
---

Codex/Gemini cross-provider reviews discover different defects; reusing cached diff from prior review causes Gemini to re-detect already-fixed defects on stale content. Each independent review dispatch requires live refetch of diff/body, not cached `/tmp/<prompt>.txt` artifacts.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
