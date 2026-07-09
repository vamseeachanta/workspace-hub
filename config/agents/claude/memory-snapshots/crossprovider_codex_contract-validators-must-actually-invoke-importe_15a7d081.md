---
name: crossprovider codex contract-validators-must-actually-invoke-importe
description: Contract validators must actually invoke imported validation, not just reference imported schemas
metadata:
  type: reference
  source: codex
  bridged: 2026-07-03
  tags: [testing, validation, contract-driven-design]
---

Validators often check that an imported schema exists (e.g., via import assertion or file existence) but skip calling the imported validator functions. This creates a false appearance of enforcement. Test by probing invalid cases per the imported contract and expecting them to fail; empty error lists reveal missing calls.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
