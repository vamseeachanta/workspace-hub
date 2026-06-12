---
name: crossprovider hermes multi-location-git-copies-require-canonicality-a
description: Multi-location Git copies require canonicality audit before placement
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [repo-placement, git-state-verification, duplicate-inventory]
---

When repos/data exist in multiple locations (sibling checkouts, nested under parent, data-bucket aliases), must probe git remote, HEAD, and dirty-state to identify canonical vs. stale/nested copies before choosing machine placement or running normalization. Choosing the wrong copy as canonical creates cleanup debt.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
