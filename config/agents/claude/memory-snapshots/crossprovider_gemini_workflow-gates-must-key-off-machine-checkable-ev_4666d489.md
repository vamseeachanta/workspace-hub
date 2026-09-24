---
name: crossprovider gemini workflow-gates-must-key-off-machine-checkable-ev
description: Workflow gates must key off machine-checkable evidence, not frontmatter fields
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [workflow, gates, verification]
---

Status fields in frontmatter (e.g., `plan_reviewed: true`) can be hand-edited and bypass gates. Executable workflow guards should verify the presence and content of structured evidence files (e.g., YAML with schema validation) rather than trusting frontmatter, because the gap between documented workflow state and actual gate enforcement is a reliable failure mode.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
