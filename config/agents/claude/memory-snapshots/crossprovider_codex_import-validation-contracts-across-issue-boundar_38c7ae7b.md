---
name: crossprovider codex import-validation-contracts-across-issue-boundar
description: Import validation contracts across issue boundaries, don't redefine
metadata:
  type: reference
  source: codex
  bridged: 2026-07-02
  tags: [multi-issue-integration, code-reuse, architecture, contract-coupling]
---

When one issue (#70) integrates another issue's (#62) validation logic, import the upstream validation functions directly rather than re-parsing or redefining the contract. This prevents schema drift, avoids duplicate validation logic, and makes the dependency explicit. Use the upstream module's validators as the source of truth.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
