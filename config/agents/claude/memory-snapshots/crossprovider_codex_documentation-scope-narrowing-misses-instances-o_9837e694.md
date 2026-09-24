---
name: crossprovider codex documentation-scope-narrowing-misses-instances-o
description: Documentation scope narrowing misses instances of same antipattern
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [documentation, audit-plans, scope-creep, stale-references]
---

Audit/cleanup plans that target specific stale references often under-scope and miss broader instances of the same problem in nearby files. Example: plan #614 targeted `python diffraction_cli.py` and specific broken links but left other stale `src/digitalmodel/modules/orcawave/` paths in the same README. Scope creep happens invisibly after implementation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
