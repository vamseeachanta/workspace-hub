---
name: crossprovider codex allowlist-only-projection-required-for-public-pr
description: Allowlist-only projection required for public/private data routing
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [security, data-routing, validation]
---

Deny-list-only checks (forbidding known private fields like `client`, `project`) miss unknown leak vectors. Public data routing must use an allowlist (whitelist) of permitted fields, with explicit tests for nested objects, citation sidecars, ledger entries, and unknown future content types.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
