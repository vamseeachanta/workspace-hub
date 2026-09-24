---
name: crossprovider codex hard-constraints-must-fail-closed-when-routing-r
description: Hard constraints must fail-closed when routing result becomes empty
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [routing, constraints, fail-closed]
---

Returning empty set after hard-constraint pruning lets downstream interpret as fallback/default, bypassing constraints. Require explicit fail-closed default or --allow-empty flag to proceed.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
