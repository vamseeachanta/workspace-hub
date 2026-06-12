---
name: crossprovider hermes failure-artifact-contracts-must-hold-on-all-exit
description: Failure-artifact contracts must hold on all exit paths
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [error-handling, schema-contract, artifact-completeness]
---

Scripts claiming to emit normalized YAML/JSON verdicts on failure must actually emit them, even on early-exit errors (e.g., command-not-found, missing bashrc). If a shell operation needed for error-handling depends on an undeclared tool, the script exits with no artifact, violating the contract.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
