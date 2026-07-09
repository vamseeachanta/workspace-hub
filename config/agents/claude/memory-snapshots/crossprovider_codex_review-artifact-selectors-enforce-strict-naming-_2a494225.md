---
name: crossprovider codex review-artifact-selectors-enforce-strict-naming-
description: Review artifact selectors enforce strict naming format; phantom artifacts fail hard
metadata:
  type: reference
  source: codex
  bridged: 2026-07-04
  tags: [workflow, artifact, governance, approval-gate]
---

Plans referencing old naming patterns (e.g., `2026-06-29-plan-54-claude.md` instead of `2026-06-29-plan-54-claude-r1.md`) or materialized artifacts that do not exist fail with hard selector errors, not warnings. Update plan artifact maps to match current format (YYYY-MM-DD-plan-<N>-<provider>-r<N>.md) and ensure all referenced files exist before marking plan for review.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
