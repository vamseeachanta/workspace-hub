---
name: crossprovider codex concurrent-draft-claims-must-match-github-issue-
description: Concurrent draft claims must match GitHub issue state
metadata:
  type: reference
  source: codex
  bridged: 2026-07-17
  tags: [issue-state, synchronization, governance, tracking]
---

If GitHub says `status:needs-plan`, don't claim `status:plan-review` in untracked draft files. Sync state explicitly—false-positive status in loose files masks actual blockers and confuses downstream work.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
