---
name: crossprovider codex track-blocker-discovery-rounds-separately-to-dis
description: Track blocker discovery rounds separately to distinguish resolved from new findings
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [review-process, regression, tracking]
---

When a plan goes through multiple review rounds (r1/r2/r3), maintain separate tracking of which blockers were found and fixed vs newly discovered. This prevents regression (old blockers resurfacing) and helps focus on unresolved issues. Compare r2 findings against r1 to confirm resolving prior blockers before approving.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
