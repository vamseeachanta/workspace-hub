---
name: crossprovider codex schema-paths-in-plans-often-diverge-from-actual-
description: Schema paths in plans often diverge from actual source nesting
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [schemas, data-models, verification]
---

Plan documentation and implementation schemas frequently differ in field nesting. Example: plan cited `asset.body.geometry.waterline_z` but actual schema nests geometry under `BodySpec.vessel.geometry`. Always verify field paths against the source schema definition before writing implementation pseudocode.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
