---
name: crossprovider codex review-artifact-filename-pattern-needs-collision
description: Review artifact filename pattern needs collision-free timestamps
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [review-automation, file-naming, ops]
---

Same-day reruns of plan reviews overwrite previous results using YYYY-MM-DD-plan-NNN-<provider>.md pattern. Collision-free form (YYYY-MM-DDTHHMMSSZ-plan-NNN-<provider>.md) required; consumer must classify both new and legacy artifact formats.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
