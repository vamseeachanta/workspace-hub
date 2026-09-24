---
name: crossprovider codex single-authoritative-inventory-source-with-expli
description: Single authoritative inventory source with explicit exception handling beats scattered declarations
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [inventory-management, single-source-of-truth, coupling]
---

Machine registry as source-of-truth, but weekly checklists may reference machines not-yet-in-registry (macbook-portable). Plans must explicitly state: 'registry is authoritative; v1 treats non-registry entries as blocked/unsupported' and declare the gap-closure plan (follow-up issue #2240).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
