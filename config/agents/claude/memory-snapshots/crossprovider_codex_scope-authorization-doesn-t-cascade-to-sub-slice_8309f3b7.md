---
name: crossprovider codex scope-authorization-doesn-t-cascade-to-sub-slice
description: Scope authorization doesn't cascade to sub-slices implicitly
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [authorization-model, scope-boundaries, meta-pattern]
---

A user-approved issue bundling multiple items ('implement A + B + C') does not auto-authorize a single slice later ('just do A'). Document explicitly that the slice is part of the bundled approval, or request new authorization. Scope boundaries are user-defined, not inferred from titles or issue state.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
