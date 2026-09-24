---
name: crossprovider codex silence-is-failure-in-adversarial-reviews
description: Silence is failure in adversarial reviews
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [review, quality-gate, adversarial-stance]
---

A plan review that finds no findings must explicitly list what was checked (file paths, sections, tool invocations). An empty review signals review-tool failure or incomplete retrieval, not plan success. Always return 'reviewed against [list] and none found' before silence.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
