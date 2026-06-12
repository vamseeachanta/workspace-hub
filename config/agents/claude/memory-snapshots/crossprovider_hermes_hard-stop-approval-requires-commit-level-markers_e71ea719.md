---
name: crossprovider hermes hard-stop-approval-requires-commit-level-markers
description: Hard-stop approval requires commit-level markers, not just labels
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [approval-workflow, governance, hard-stop]
---

GitHub labels alone are insufficient for safe autonomous execution. Approval gates must verify: canonical plan file, clean multi-provider review artifacts with matching plan SHA, clean GitHub labels, and a committed numeric local marker (e.g., `.planning/plan-approved/<issue>.md`). Missing any of these must block execution, not degrade gracefully.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
