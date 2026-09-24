---
name: crossprovider codex import-stable-contracts-over-copying-definitions
description: Import stable contracts over copying definitions
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [architecture, maintenance, contracts, drift-detection]
---

When a component depends on stable upstream definitions (field lists, validators, enums), import them from the source module instead of copying. Imports catch drift automatically at import time; copies enable silent divergence.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
