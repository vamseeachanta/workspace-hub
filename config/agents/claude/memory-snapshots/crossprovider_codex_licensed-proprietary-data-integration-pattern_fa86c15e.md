---
name: crossprovider codex licensed-proprietary-data-integration-pattern
description: Licensed proprietary data integration pattern
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [data-handling, licensing, proprietary-data]
---

When code must access licensed workbooks (e.g., `/mnt/ace/mkt-a-codes/OCIMF/OCIMF Coef.xlsx`): use a fail-closed preflight check, emit a pointer-only citation (not the full path), track a provenance README in the repo, and never commit the coefficient corpus itself. Row fields and test assertions can reference extracted values, but the source workbook stays off-repo. Applied in #2760 proj-a current-rudder implementation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
