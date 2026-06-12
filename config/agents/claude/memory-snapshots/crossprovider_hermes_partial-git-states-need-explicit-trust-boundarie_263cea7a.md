---
name: crossprovider hermes partial-git-states-need-explicit-trust-boundarie
description: Partial git states need explicit trust boundaries in audit reports
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [partial-repo-state, sparse-checkout, test-coverage]
---

Sparse-checkout or offline inventory states can create false loss-risk counts if tracked-set is empty. Suppress all `filesystem_only` and `missing_tracked` findings when trust is untrusted; test coverage must include this path, not just happy path.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
