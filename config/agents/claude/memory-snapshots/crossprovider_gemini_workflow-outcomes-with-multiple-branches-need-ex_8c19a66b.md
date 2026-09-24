---
name: crossprovider gemini workflow-outcomes-with-multiple-branches-need-ex
description: Workflow outcomes with multiple branches need explicit decision tables
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [workflow, gates, design]
---

When a workflow gate has multiple possible outcomes (approve, revise, reject, no-response), the decision logic should be explicitly documented as a decision table (structured data, not prose) and made machine-checkable by the verification script. Implicit prose logic leads to misinterpretation and inconsistent enforcement.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
