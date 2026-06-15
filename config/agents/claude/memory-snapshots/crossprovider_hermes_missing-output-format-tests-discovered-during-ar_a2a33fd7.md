---
name: crossprovider hermes missing-output-format-tests-discovered-during-ar
description: Missing output-format tests discovered during artifact generation
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [output-formats, test-coverage, artifact-routes, acceptance-criteria]
---

proj-a tests validated HTML/PDF output but did not cover DOCX. When artifact-generation phase arrived, DOCX route was unimplemented and untested. Acceptance tests must enumerate ALL required output formats upfront, not defer format coverage to implementation phase.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
