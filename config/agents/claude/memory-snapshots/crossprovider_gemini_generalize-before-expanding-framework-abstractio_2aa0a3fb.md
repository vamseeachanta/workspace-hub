---
name: crossprovider gemini generalize-before-expanding-framework-abstractio
description: Generalize before expanding: framework abstraction for autoresearch-like loops
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [architecture, automation, design-pattern, refactoring, testing]
---

A single-purpose loop (like skill-autoresearch) should be generalized into a pluggable framework with target-type discovery and evaluation contracts *before* adding support for new target types (agents, templates, workflow configs). This prevents code duplication, unifies results tracking, and simplifies testing across target types.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
