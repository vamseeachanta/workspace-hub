---
name: crossprovider codex numeric-bounds-enforcement-makes-bounded-discove
description: Numeric bounds enforcement makes bounded discovery testable
metadata:
  type: reference
  source: codex
  bridged: 2026-07-09
  tags: [testing, verification, bounds-checking, discovery]
---

Soft guidance ('use reasonable limits') fails because implementations can crawl unbounded while passing review. Bounded discovery requires explicit numeric caps: max depth, max entries per root, per-root timeout, no symlink following. Write tests that fail if caps are exceeded; these tests must verify bounds are enforced, not just that output looks good.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
