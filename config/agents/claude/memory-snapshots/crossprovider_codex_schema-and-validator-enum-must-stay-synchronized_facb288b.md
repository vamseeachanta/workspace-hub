---
name: crossprovider codex schema-and-validator-enum-must-stay-synchronized
description: Schema and Validator Enum Must Stay Synchronized
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [schema-drift, documentation, code-generation]
---

Schema documentation can drift from validator rules (e.g., schema names `standard`/`source`/`external-public` but validator actually accepts `core`/`external`/`unresolved`), causing false validator passes. Keep schema enum values and validator accept-lists in sync; consider code-generating one from the other to prevent drift.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
