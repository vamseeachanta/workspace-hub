---
name: crossprovider codex environmental-host-blocker-checking-is-load-bear
description: Environmental/host blocker checking is load-bearing
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [gates, blockers, governance]
---

Before starting any implementation, verify gate + host availability (licensed-win-1, Blender binary, OrcaFlex runtime, data prerequisites). If blocked, post a GitHub comment with evidence and stop—no code changes. Multiple issues (#2229, #1264, #2055) demonstrate that skipping this check wastes session time.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
