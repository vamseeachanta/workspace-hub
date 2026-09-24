---
name: crossprovider gemini config-schema-migration-failures-in-version-upda
description: Config schema migration failures in version updates are a primary breakage vector
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [tool-updates, configuration-management, schema-evolution, failure-modes]
---

Tool version bumps frequently include config schema changes. These must be validated separately from binary updates; config-related breakage is often silent (tool runs but fails on first real operation). Track schema migrations explicitly in update scripts.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
