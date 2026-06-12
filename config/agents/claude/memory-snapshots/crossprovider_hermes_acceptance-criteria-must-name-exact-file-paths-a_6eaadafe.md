---
name: crossprovider hermes acceptance-criteria-must-name-exact-file-paths-a
description: Acceptance criteria must name exact file paths and command sets
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [acceptance-criteria, planning, governance]
---

Vague criteria like 'produces expected output families' or 'failures are classified' are unmeasurable and cause reviewer confusion. AC entries must specify exact artifact paths (e.g., digitalmodel/docs/validation/2026-04-30-*.md), file formats, git SHAs, Python/uv versions, and the exact commands that must exit 0. Metrics and thresholds must be quantified.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
