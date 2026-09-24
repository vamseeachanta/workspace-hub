---
name: crossprovider codex ci-trigger-scopes-must-be-defined-consistently-a
description: CI trigger scopes must be defined consistently across all plan sections
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [ci-workflows, scope, triggers]
---

When Deliverable claims "scope to src/ + tests/ only" but Detailed Spec uses broad `paths-ignore` negation, or when file lists in triggers contradict acceptance criteria file scoping, the plan is internally false. All sections (title, Deliverable, Acceptance, Spec, Files to Change) must agree on what triggers CI and what files change.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
