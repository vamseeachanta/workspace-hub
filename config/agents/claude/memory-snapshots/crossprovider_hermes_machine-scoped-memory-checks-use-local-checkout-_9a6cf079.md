---
name: crossprovider hermes machine-scoped-memory-checks-use-local-checkout-
description: Machine-scoped memory checks use local checkout context
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [cross-machine-execution, verification-scope, hidden-failure-modes]
---

Issue #2775: `build_report(machine_name)` resolves target machine but `run_memory_check(root)` still shells out to local repo, reading HOME/.hermes and repo-local agents.md. Cross-machine verification reports false positives; dev-secondary checks report local path instead of workspace root.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
