---
name: crossprovider codex enforcement-guards-break-silently-on-refactoring
description: Enforcement guards break silently on refactoring
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [infrastructure, enforcement, coverage-hazard, silent-failure]
---

File-enumeration-based guards (checking for specific filenames like CLAUDE.md) lose coverage when files are moved or renamed, with zero signal that coverage dropped. Deriving membership from build scripts moves coupling but does not solve the silent-loss hazard. Need explicit registry + test assertions against complete coverage set, not derived membership.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
