---
name: crossprovider hermes off-repo-licensed-source-integration-pattern
description: Off-repo licensed source integration pattern
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [licensed-source, source-gates, off-repo, test-driven]
---

For proprietary workbooks (OCIMF coefficients, licensed specs), read programmatically from off-repo paths (e.g., `/mnt/ace/mkt-a-codes/OCIMF/OCIMF Coef.xlsx`); enforce source-ID gates in tests (e.g., `ocimf-meg3-current-coefficients`, `ocimf-meg4-current-coefficients`); never commit raw workbooks or extracted coefficient corpora.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
