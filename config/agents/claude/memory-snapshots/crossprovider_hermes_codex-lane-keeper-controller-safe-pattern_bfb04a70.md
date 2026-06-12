---
name: crossprovider hermes codex-lane-keeper-controller-safe-pattern
description: Codex lane-keeper controller safe pattern
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [codex-operations, lane-management, automation, git-safety]
---

Autonomous lane-keeper must not merge/close/label; it monitors and tops up approved work. Parent process filtering (not child duplicates) determines active lane count. Branch/head inspection uses `timeout 10 git` to prevent hangs on large repos. Ready branches left for interactive review.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
