---
name: crossprovider hermes check-fallback-artifact-paths-when-prescribed-pa
description: Check fallback artifact paths when prescribed paths unused
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [artifact-paths, agent-operations, failure-diagnosis]
---

When agents don't write to prescribed paths (e.g., agent-logs/results/), check standard fallback locations (docs/sessions/, etc.) for actual outputs before assuming operation failed or output is missing.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
