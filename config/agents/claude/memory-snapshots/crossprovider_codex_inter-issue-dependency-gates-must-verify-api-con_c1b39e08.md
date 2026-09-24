---
name: crossprovider codex inter-issue-dependency-gates-must-verify-api-con
description: Inter-issue dependency gates must verify API contracts
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [planning, dependencies, api-contracts]
---

Checking if mesh_preflight.py exists doesn't guarantee required helper functions are exported. Use function signature specs or integration tests as stronger gates than file existence checks.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
