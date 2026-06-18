---
name: crossprovider codex data-contract-fields-must-be-internally-consiste
description: Data contract fields must be internally consistent
metadata:
  type: reference
  source: codex
  bridged: 2026-06-16
  tags: [schema, contract, validation, design]
---

A field cannot be required to hold both regulator sources AND official publisher URLs. Either define separate fields, enforce mutual exclusion, or explicitly document which constraint is primary.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
