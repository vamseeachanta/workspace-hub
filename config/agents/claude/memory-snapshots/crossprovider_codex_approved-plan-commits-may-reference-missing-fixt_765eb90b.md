---
name: crossprovider codex approved-plan-commits-may-reference-missing-fixt
description: Approved plan commits may reference missing fixtures
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [planning, approval-gates, prerequisites]
---

Plan approval doesn't guarantee referenced files are present in the approved commit. Verify pre-landed fixtures actually exist in the approved plan SHA before proceeding; missing fixtures may require blocking or re-scoping.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
