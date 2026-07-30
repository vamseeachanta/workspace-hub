---
name: crossprovider codex explicit-none-vs-empty-list-semantics-collapse-u
description: Explicit `None` vs empty-list semantics collapse under `x or default`
metadata:
  type: reference
  source: codex
  bridged: 2026-07-12
  tags: [semantics, api-design, testing]
---

Using `entries or [_entry()]` treats both `None` and `[]` identically. If the API must distinguish them (e.g., `None` means use default, `[]` means no entries), use explicit `entries if entries is not None else [_entry()]`.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
