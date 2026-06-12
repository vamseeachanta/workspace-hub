---
name: crossprovider codex large-remediation-work-requires-pre-source-durab
description: Large remediation work requires pre-source durable inventory artifact
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [remediation-workflow, inventory-gating]
---

For multi-wave code cleanup (e.g., flake8 debt, linting), checking in a grouped, rule-family inventory report before source edits begin is a gate condition. Transient `/tmp` snapshots are insufficient; artifact must be version-controlled in the repo target.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
