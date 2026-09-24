---
name: crossprovider gemini inferred-signals-do-not-satisfy-measured-complia
description: Inferred signals do not satisfy measured compliance
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [workflow-governance, signal-compliance, measurement]
---

Only explicit stage signals emitted by scripts/logging count toward compliance reporting. Inferred signals (detected through analysis but not explicitly emitted) are diagnostic only and do not satisfy gate-signal-coverage requirements. This distinction matters for cross-agent workflow audits.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
