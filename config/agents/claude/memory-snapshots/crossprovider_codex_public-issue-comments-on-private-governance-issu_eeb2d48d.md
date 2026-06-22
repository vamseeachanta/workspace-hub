---
name: crossprovider codex public-issue-comments-on-private-governance-issu
description: Public issue comments on private-governance issues need mechanical safety gates
metadata:
  type: reference
  source: codex
  bridged: 2026-06-21
  tags: [privacy, github-api, safety-gate]
---

Closing privacy-scoped GitHub issues with public comments risks leaking sensitive details (raw labels, filenames, client IDs, source text). The plan must either enforce pre-approved comment templates, scan generated comments via linter, or skip comments entirely. Manual adherence is insufficient for sensitive boundaries.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
