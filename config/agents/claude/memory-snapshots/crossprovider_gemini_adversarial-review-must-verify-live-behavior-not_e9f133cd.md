---
name: crossprovider gemini adversarial-review-must-verify-live-behavior-not
description: Adversarial review must verify live behavior, not just documented intent
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [review, governance, verification]
---

Reviews that only read documentation miss real failures—enforcement hooks often have undocumented bypass vectors, documented features that are inert, or safe-path exemptions that are too broad. Cross-check actual hook/script output against documented behavior.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
