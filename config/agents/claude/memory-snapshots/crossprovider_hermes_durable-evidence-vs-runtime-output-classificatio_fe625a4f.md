---
name: crossprovider hermes durable-evidence-vs-runtime-output-classificatio
description: Durable evidence vs runtime output classification creates contradictions
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [artifact-classification, refactoring-safety, scope-locking]
---

Distinguishing committed reports (e.g., docs/examples/b1528-report.html) from runtime outputs (generated in ignored dirs) breaks down if source code still references or generates the old paths. Requires explicit exception handling: lock which files change, allow documented runtime refs, defer per-file relocation to follow-ups with concrete issue IDs.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
