---
name: crossprovider codex stale-or-conflicting-infrastructure-docs-are-rev
description: Stale or conflicting infrastructure docs are review gates
metadata:
  type: reference
  source: codex
  bridged: 2026-07-09
  tags: [review, governance, documentation, correctness]
---

When a plan's investigation reveals outdated or contradictory infrastructure documentation (e.g., DATA_RESIDENCE_POLICY claims vs actual setup scripts), gate the implementation on either fixing those docs or explicitly declaring the conflict in the plan. Deferring to follow-on work leaves stale docs in place and invites future inconsistency bugs.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
