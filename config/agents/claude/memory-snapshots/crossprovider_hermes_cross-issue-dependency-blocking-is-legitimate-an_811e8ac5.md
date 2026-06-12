---
name: crossprovider hermes cross-issue-dependency-blocking-is-legitimate-an
description: Cross-issue dependency blocking is legitimate and should be documented
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [dependency-blocking, migration-patterns, blocker-documentation]
---

When a bundle cannot complete an issue because legacy code is still needed by production (e.g., old API not yet fully migrated), document the blocker on the issue with the specific dependency and leave it open. Codex correctly avoided removing legacy code when royalty citation contract was not yet wired, preventing silent breakage.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
