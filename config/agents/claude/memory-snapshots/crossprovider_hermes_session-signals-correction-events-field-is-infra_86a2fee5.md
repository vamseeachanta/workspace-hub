---
name: crossprovider hermes session-signals-correction-events-field-is-infra
description: Session signals correction_events field is infrastructure but no collection pipeline
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [memory-system, skill-promotion, hermes-pipeline, infrastructure-gap]
---

The session signals schema includes a correction_events field for capturing user corrections ("remember this", "fix this"), but the pipeline to populate it from session transcripts is not wired. This blocks the correction-to-skill promotion workflow, which currently captures ~0% of eligible learnings (target 40%). Enabling this collection requires connecting the session→signals ETL step.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
