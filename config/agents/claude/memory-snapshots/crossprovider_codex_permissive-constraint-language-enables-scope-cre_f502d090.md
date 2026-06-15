---
name: crossprovider codex permissive-constraint-language-enables-scope-cre
description: Permissive constraint language enables scope creep
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [scope-control, requirements-review, spec-clarity]
---

Phrases like 'unless implementation decides', 'may include if needed', or 'optional unless required' in scope constraints create escape hatches that allow scope expansion at implementation time. Audit constraint text explicitly for permissive language; tighten to 'out of scope' or 'deferred to issue #X' without conditional clauses.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
