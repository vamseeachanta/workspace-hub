---
name: crossprovider codex cross-plan-api-seams-require-pre-signed-contract
description: Cross-plan API seams require pre-signed contracts; don't invent hooks in dependent plans
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [architecture, api-design, planning]
---

Plan #606 invented a `preparer=` hook for Plan #605's `resolve_assets()` that #605 never defined, creating a seam that doesn't exist. When Plan A calls Plan B's API, Plan B must define the full signature (including optional hooks) before Plan A writes pseudocode that invokes them. Validate upstream contract exhaustively before assuming integration points.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
