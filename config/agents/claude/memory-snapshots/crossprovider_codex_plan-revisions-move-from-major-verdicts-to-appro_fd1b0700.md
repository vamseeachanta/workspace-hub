---
name: crossprovider codex plan-revisions-move-from-major-verdicts-to-appro
description: Plan revisions move from MAJOR verdicts to APPROVE when they add explicit test names, artifact paths, and per-artifact enforcement gates
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [code-review, planning, revision-cycles, test-driven-scope]
---

r1 findings ('raw path leakage', 'missing taxonomy gate') become approvable in r2 when revised plans specify test function names and per-artifact scan locations (e.g., 'test_extraction_sanitizes_frontmatter_source_id'). Specificity enables adversarial verification.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
