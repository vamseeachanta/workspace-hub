---
name: crossprovider codex oauth-scope-gates-remote-absence-proofs
description: OAuth scope gates remote-absence proofs
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [oauth, verification, security]
---

Classic `repo` scope is required to distinguish "404 due to no access" from "404 because absent"; owner login alone cannot prove access to every private repo. Absence proof requires scoped credential validation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
