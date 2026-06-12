---
name: crossprovider codex git-submodule-foreach-hangs-on-broken-submodules
description: git submodule foreach hangs on broken submodules; use status instead
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [git, scripting, operational]
---

git submodule foreach can hang indefinitely on detached or broken submodules. For read-only enumeration, use git submodule status + awk instead. Wrap per-repo operations in timeouts to prevent cascading hangs.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
