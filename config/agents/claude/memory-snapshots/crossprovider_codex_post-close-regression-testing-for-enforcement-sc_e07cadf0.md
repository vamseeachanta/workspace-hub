---
name: crossprovider codex post-close-regression-testing-for-enforcement-sc
description: Post-close regression testing for enforcement scripts catches build/check parity misses
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [enforcement-scripts, testing]
---

When build and check tools diverge post-close (e.g., builder appends extras but checker doesn't rebuild them), regression tests pinned in the plan can catch those misses before they cause silent failures.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
