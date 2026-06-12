---
name: crossprovider codex wiki-ingest-verification-gates-before-completion
description: Wiki ingest verification gates before completion
metadata:
  type: reference
  source: codex
  bridged: 2026-05-28
  tags: [standards-ingest, verification]
---

Before reporting completion: run frontmatter/link probe, conflict-marker check (scripts/enforcement/), git diff --check, verify cross-link targets exist. Do not git add/commit/push; report PASS/FAIL. Missing scripts handled gracefully with fallback ad-hoc validation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
