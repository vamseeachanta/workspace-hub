---
name: crossprovider gemini 20-stage-workflow-pattern-yaml-contract-micro-sk
description: 20-stage workflow pattern: YAML contract + micro-skill per stage
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [workflow-design, stage-contracts, micro-skills]
---

Each stage defined by YAML contract (≤15 lines: order, weight, invocation mode, human gates, entry/exit artifacts) + micro-skill (≤20 lines: checklist, entry artifacts, exit artifacts). Enables repeatable multi-stage workflows with clear stage boundaries.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
