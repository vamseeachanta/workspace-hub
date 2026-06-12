---
name: crossprovider codex plan-blocking-dependencies-must-name-the-blocker
description: Plan blocking dependencies must name the blocker explicitly
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [planning, dependencies, blocking]
---

Scheduler/operational plans that depend on other governance changes (e.g., #2763 blocked on #2762 scheduler routing contract) must name the blocker and exit code 2 during implementation if the dependency is missing. Do not hardcode unlanded CLI flags or assume later landing; make the blocker obvious.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
