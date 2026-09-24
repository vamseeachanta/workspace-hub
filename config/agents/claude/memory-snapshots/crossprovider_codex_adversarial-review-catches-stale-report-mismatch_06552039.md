---
name: crossprovider codex adversarial-review-catches-stale-report-mismatch
description: Adversarial review catches stale report mismatches
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [review, reporting, consistency]
---

Implementation may commit successfully but task report doesn't update—review against both diff and expected report state catches this inconsistency. Report claiming 'BLOCKED, no commit' while actual commit SHA exists in diff is a critical mismatch revealing scope creep or incomplete closeout.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
