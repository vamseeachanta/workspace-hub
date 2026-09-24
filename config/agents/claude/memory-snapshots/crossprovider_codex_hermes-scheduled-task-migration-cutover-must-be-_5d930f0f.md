---
name: crossprovider codex hermes-scheduled-task-migration-cutover-must-be-
description: Hermes → scheduled-task migration cutover must be immediate, not deferred to future runs
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [scheduled-tasks, hermes-migration, cutover-timing]
---

Plans that migrate from Hermes cron to scheduled tasks need explicit removal/disablement of the old cron after first successful run, not deferred until "after 5+ runs confirm behavior." Deferral creates a dual-source-of-truth security risk. Cutover timing should be part of the implementation checklist.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
