---
name: crossprovider hermes multi-provider-adversarial-review-gemini-first-t
description: Multi-provider adversarial review: Gemini first, then Codex re-review
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [review, multi-provider, quality-gate]
---

When Codex returns MAJOR on second review (re-review pattern), dispatch Gemini re-review after fixes are applied. Codex and Gemini find non-overlapping defect classes; Codex re-review after fixes is a reliable gate. Large argv dispatch (shell "Argument list too long") may still block Gemini dispatch—use file-based temp artifacts for re-review bodies.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
