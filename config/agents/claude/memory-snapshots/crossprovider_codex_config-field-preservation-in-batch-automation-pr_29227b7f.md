---
name: crossprovider codex config-field-preservation-in-batch-automation-pr
description: Config field preservation in batch automation prevents reproducibility drift
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [automation, config-management, workflows]
---

Batch workflows (fills, domains, prebuilt geometry, mesh state) must carry full parametric state. Dropping config fields during dispatch (motion, domain initialization, geometry prebuilt flags) silently breaks reproducibility. Config preservation is non-obvious and must be explicit in workflow contracts.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
