---
name: crossprovider codex standards-naming-requires-grep-grounding-in-code
description: Standards naming requires grep-grounding in code, not prose
metadata:
  type: reference
  source: codex
  bridged: 2026-07-07
  tags: [standards, documentation, validation]
---

Every standard named in docs (API/DNV/ASME) must be grep-matched to a linked implementation or reference; prose claims in PR bodies rot. Use this discipline to prevent standards overclaim drift, as demonstrated by #1391 fatigue section.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
