---
name: crossprovider codex script-reuse-is-preferred-over-new-implementatio
description: Script reuse is preferred over new implementation
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [architecture, reuse, efficiency]
---

When new functionality needs an execution engine, prioritize reusing existing scripts (e.g., run-openfoam-tutorials.sh) as 'the strongest execution engine to reuse.' This avoids duplication, leverages tested code, and reduces surface area for bugs.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
