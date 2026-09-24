---
name: crossprovider codex defensive-migration-gates-with-structural-assert
description: Defensive migration gates with structural assertions
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [gates, configuration-safety, migration-patterns]
---

When a tool must refuse unsafe configurations (e.g., migration applying canonical paths), guard with explicit structural assertions (`is_dir()`, parse-equality checks), not conditional logging. Example: pathnorm migration refuses to apply `enabled:true` on canonical DDE roots to prevent live mixed-path states. Structural check > heuristic denial.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
