---
name: crossprovider codex spec-template-docs-references-must-be-exact-file
description: Spec/template docs references must be exact file paths
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [documentation, templates, spec-design]
---

Templates and specs referencing supporting documentation should link to exact file paths (.claude/docs/orchestrator-pattern.md, specs/modules/fea-checklist.md) not loose names ('see docs on orchestration'). Loose references break author navigation and AC traceability; exact paths make specs self-service.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
