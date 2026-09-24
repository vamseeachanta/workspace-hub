---
name: crossprovider codex compose-upstream-validators-instead-of-re-implem
description: Compose upstream validators instead of re-implementing local variants
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [validator-design, code-reuse, ci]
---

When split issues delegate scanning behavior, call/compose existing parent validators (e.g., --scan-public-path flag) rather than rebuilding local equivalents. Reduces defect surface and keeps CI repo-local.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
