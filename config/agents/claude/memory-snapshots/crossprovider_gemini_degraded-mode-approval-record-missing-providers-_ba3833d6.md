---
name: crossprovider gemini degraded-mode-approval-record-missing-providers-
description: Degraded-mode approval: record missing providers and approval scope explicitly
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [workflow-gates, multi-provider, fault-tolerance]
---

When multi-provider workflows degrade (e.g., 3→2 provider fallback due to outage), store `missing_providers`, `approval_scope`, and `approved_by` explicitly in evidence YAML. This lets automation and reviewers distinguish degraded-mode approvals from full-strength ones, enabling conditional downstream behavior.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
