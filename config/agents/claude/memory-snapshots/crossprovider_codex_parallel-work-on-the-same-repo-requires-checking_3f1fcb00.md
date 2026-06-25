---
name: crossprovider codex parallel-work-on-the-same-repo-requires-checking
description: Parallel work on the same repo requires checking reflog and uncommitted state before starting
metadata:
  type: reference
  source: codex
  bridged: 2026-06-24
  tags: [parallel-sessions, detached-head-hazard, pre-flight-checks]
---

Before implementing a feature based on a detached-HEAD or off-main state, check `git log --oneline` to see if a parallel session has already merged that work to main, and check `git status` for uncommitted changes that a parallel session might be still working on. A 154+ commit divergence from main is a red flag that something upstream has moved.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
