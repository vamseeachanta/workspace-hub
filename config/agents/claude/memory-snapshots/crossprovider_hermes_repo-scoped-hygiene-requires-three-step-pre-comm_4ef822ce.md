---
name: crossprovider hermes repo-scoped-hygiene-requires-three-step-pre-comm
description: Repo-scoped hygiene requires three-step pre-commit inventory pattern
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [git-hygiene, multi-repo, risk-mitigation]
---

Before staging/committing: (1) inventory dirty state, (2) classify as task-owned vs user vs session churn, (3) stage only relevant files. Prevents cross-repo pollution where tier-1 edits leak into root or vice versa.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
