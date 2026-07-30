---
name: crossprovider codex preserve-in-flight-changes-instead-of-reverting-
description: Preserve in-flight changes instead of reverting in active shared repos
metadata:
  type: reference
  source: codex
  bridged: 2026-07-10
  tags: [workflow, shared-repo, conflict-prevention]
---

When multiple features are in-flight across the same repository, work around existing changes rather than reverting them. Reverting breaks parallel work; instead, isolate your edits to non-conflicting paths and coordinate boundaries explicitly.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
