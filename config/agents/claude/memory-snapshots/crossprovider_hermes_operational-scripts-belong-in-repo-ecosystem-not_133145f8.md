---
name: crossprovider hermes operational-scripts-belong-in-repo-ecosystem-not
description: Operational scripts belong in repo ecosystem, not /tmp or /mnt scratch
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [repo-governance, script-management]
---

User directive: all launch/readiness scripts and prompts must be saved under `docs/plans/machine-prompts/` and `scripts/operations/agent-execution/`, not in /tmp or /mnt/local-analysis scratch directories. Runtime logs stay in /mnt/local-analysis; artifacts stay in repo for reproducibility.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
