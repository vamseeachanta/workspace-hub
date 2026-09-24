---
name: crossprovider gemini plan-branch-convention-is-optional-not-mandatory
description: Plan-branch convention is optional, not mandatory
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [planning, workflow, approval-gate]
---

The `plan/issue-*` branch pattern is used by some workspace lanes but NOT a required part of the approval contract. Plan approval requires `status:plan-approved` label + `.planning/plan-approved/<NNN>.md` marker; a separate plan branch is optional.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
