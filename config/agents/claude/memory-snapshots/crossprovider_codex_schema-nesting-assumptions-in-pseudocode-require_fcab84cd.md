---
name: crossprovider codex schema-nesting-assumptions-in-pseudocode-require
description: Schema nesting assumptions in pseudocode require early verification
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [schema-contracts, pseudocode-validation]
---

Plans often embed schema assumptions in pseudocode (e.g., `asset.body.geometry.waterline_z`) without verifying the actual nesting exists. Grepping the schema before pseudocode prevents implementation traps where the plan's assumed path diverges from the real schema (e.g., geometry nested under `vessel`, not `body`).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
