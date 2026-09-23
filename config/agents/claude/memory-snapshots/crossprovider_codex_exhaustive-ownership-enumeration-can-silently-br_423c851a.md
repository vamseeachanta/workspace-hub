---
name: crossprovider codex exhaustive-ownership-enumeration-can-silently-br
description: Exhaustive ownership enumeration can silently break on inheritance
metadata:
  type: reference
  source: codex
  bridged: 2026-07-19
  tags: [contract-composition, ownership-tracking, versioning]
---

A rule like "every child issue has exactly one crosswalk entry" can be true for the *listed* entries while inherited blocking children are omitted from the enumeration. Composition logic must verify completeness against the union of base + v3 children, not just listed ones.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
