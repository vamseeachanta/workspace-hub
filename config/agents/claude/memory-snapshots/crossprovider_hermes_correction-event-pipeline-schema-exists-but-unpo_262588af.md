---
name: crossprovider hermes correction-event-pipeline-schema-exists-but-unpo
description: Correction event pipeline schema exists but unpopulated
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [skills, pipeline-gap, data-capture]
---

session-signals JSONL files have correction_events field but it's always empty. The schema exists but the capture pipeline is not wired. This blocks the skill-promotion goal (target 40% conversion). Before building promotion pipeline, first wire the correction capture (user corrections, 'remember this' statements, preference signals).

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
