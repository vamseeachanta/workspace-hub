---
name: crossprovider codex explicit-capability-declaration-for-scheduled-ta
description: Explicit capability declaration for scheduled-task dependencies
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [scheduled-tasks, infrastructure, dependency-management]
---

Issue #2550 pattern: declare `jq` as an explicit capability in `schedule-tasks.yaml` rather than relying on ambiguous `gh --jq` behavior. Makes dependencies explicit, avoids silent failures, and simplifies dry-run verification.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
