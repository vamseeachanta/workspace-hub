---
name: crossprovider codex completeness-verification-uses-a-label-issue-bod
description: Completeness verification uses a label+issue-body pattern, not just external artifact files
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [completeness-gates, issue-body-driven, closeout-preflight]
---

The pattern in this codebase is gate:completeness label + owner-applied status:completeness-verified + fresh issue-body fenced JSON with embedded completeness record. Before closing an issue, the completeness score must exist in the issue body itself (not just in docs/reports/), and the enforcement script check-completeness-before-close.sh verifies the issue-body record, not external files. Acceptance criteria and closeout preflight must reference the issue-body stamp.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
