---
name: crossprovider codex already-implemented-boundaries-are-non-negotiabl
description: Already-implemented boundaries are non-negotiable
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [dependencies, scope-management, design]
---

When a new plan depends on or interacts with an already-implemented constraint (e.g., existing scanner semantics, config file rules), the plan must treat that as a fixed boundary and use it unchanged. Redesigning inherited constraints creates scope creep and divergence.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
