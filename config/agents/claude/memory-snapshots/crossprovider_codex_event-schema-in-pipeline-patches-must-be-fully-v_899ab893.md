---
name: crossprovider codex event-schema-in-pipeline-patches-must-be-fully-v
description: Event schema in pipeline patches must be fully verified against actual corpus
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [plan-review, codex-pattern, event-driven-systems, pipeline-integration]
---

Plans claiming to add new events to a pipeline (e.g., 'emit gate_compliance_score to .claude/state/session-signals') must specify exact field names and identify the consumer that reads them. Do not trust pseudocode; verify fields actually exist in the observed event corpus and that the consumer loop handles the new shape correctly. Unverified fields = MAJOR.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
