---
name: crossprovider gemini gemini-finds-non-overlapping-defects-vs-claude-i
description: Gemini finds non-overlapping defects vs Claude in cross-review
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [cross-review, adversarial-review, defect-classes]
---

Gemini's adversarial reviews surface race-condition patterns, unmeasurable acceptance criteria ('documented explanation' is not mechanically verifiable), and schema underspecification gaps that Claude self-review often misses. Three-agent cross-review (Claude + Codex + Gemini) converges to approval faster than single-agent iteration.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
