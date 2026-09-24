---
name: crossprovider codex data-contract-safety-checks-must-use-concrete-de
description: Data-contract safety checks must use concrete deny-lists, not placeholder markers
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [data-contract, safety-gate, codex-pattern]
---

Plans using placeholder markers like `"private-root prefix"` or `"certification wording"` instead of explicit deny-lists (e.g., `/mnt/`, `/home/`, `certified`, `regulatory approval`) are incomplete. Add field guards and concrete term lists to tests. Placeholder markers fail to catch real violations.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
