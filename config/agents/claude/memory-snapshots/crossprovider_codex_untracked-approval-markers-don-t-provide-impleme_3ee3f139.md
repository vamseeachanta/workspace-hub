---
name: crossprovider codex untracked-approval-markers-don-t-provide-impleme
description: Untracked approval markers don't provide implementation authority
metadata:
  type: reference
  source: codex
  bridged: 2026-07-17
  tags: [approval, governance, git, provenance]
---

Approval provenance must be versioned in git history or GitHub labels, not left in untracked files. A plan marked `.planning/plan-approved/` but untracked disappeared in a fresh checkout, while the tracked plan remained `DRAFT — NOT APPROVED` despite the loose marker. Use labels or commits.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
