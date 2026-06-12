---
name: crossprovider hermes artifact-supersession-rules-must-distinguish-aud
description: Artifact supersession rules must distinguish audit vs. eligible artifacts
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [artifact-management, pipeline-design, conflict-resolution]
---

When preserving historical review artifacts and regenerating on plan changes, must explicitly define which older artifacts remain audit-only diagnostics vs. which can be superseded by newer same-issue/provider artifacts without triggering conflict blocks. Otherwise regeneration deadlocks the pipeline with unavoidable multiple-artifact conflicts. Identified in #2502 plan-review workflow.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
