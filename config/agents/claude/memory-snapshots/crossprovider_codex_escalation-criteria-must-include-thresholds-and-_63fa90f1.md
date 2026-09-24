---
name: crossprovider codex escalation-criteria-must-include-thresholds-and-
description: Escalation criteria must include thresholds and tie-break rules
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [governance, policy, escalation, decision-rules]
---

Abstract escalation rules ('needs human review', 'high severity') become catch-all buckets that hide policy weakness. Escalation logic requires explicit thresholds (e.g., 'severity >= 3 AND confidence >= 0.8') and tie-break order (precedence when signals conflict) to prevent subjective churn.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
