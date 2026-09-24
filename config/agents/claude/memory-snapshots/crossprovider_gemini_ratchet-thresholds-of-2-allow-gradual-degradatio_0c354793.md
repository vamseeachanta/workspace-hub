---
name: crossprovider gemini ratchet-thresholds-of-2-allow-gradual-degradatio
description: Ratchet thresholds of -2% allow gradual degradation
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [ratchet, enforcement, coverage, testing]
---

A coverage or metric ratchet that permits drops (e.g., -2%) creates a boiling-frog scenario: degradation is imperceptible per-commit but accumulates over time. Stricter thresholds (0% or -0.1%) prevent erosion and keep enforcement meaningful.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
