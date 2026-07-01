---
name: crossprovider codex plan-writing-skill-output-constraints-must-overr
description: Plan-writing skill output constraints must override skill defaults when scope is narrower
metadata:
  type: reference
  source: codex
  bridged: 2026-06-30
  tags: [skill-usage, scope-management, workflow]
---

Generic planning skill defaults to 'write file to disk' and 'create GitHub comment', which conflicts with read-only scope. Use skill's section structure and completeness discipline (no placeholders, TDD sections, artifact map), but explicitly apply custom output constraints (draft in chat only, no file/comment mutations). Mismatch causes accidental scope creep.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
