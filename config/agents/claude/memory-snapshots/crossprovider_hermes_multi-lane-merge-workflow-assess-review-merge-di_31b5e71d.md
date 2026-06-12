---
name: crossprovider hermes multi-lane-merge-workflow-assess-review-merge-di
description: Multi-lane merge workflow: assess → review → merge → dispatch next wave
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [workflow, merge-coordination]
---

Workflow for provider lane completion: assess branch state → run multi-provider adversarial review (Claude/Codex/Gemini) → merge ready branches → free capacity → dispatch next wave. Do not block next-wave dispatch on slow/running lanes.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
