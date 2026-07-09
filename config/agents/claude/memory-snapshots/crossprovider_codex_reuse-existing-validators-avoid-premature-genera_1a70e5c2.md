---
name: crossprovider codex reuse-existing-validators-avoid-premature-genera
description: Reuse existing validators, avoid premature generalization
metadata:
  type: reference
  source: codex
  bridged: 2026-07-01
  tags: [architecture, code-reuse, scanner-design]
---

When adding a narrowly-scoped feature needing validation (e.g., #67 firewall), import parent validators by explicit path rather than creating generalized scanners. Keeps ownership clear and avoids bloating scope. #67 reuses #65 schema and parent coordination validator.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
