---
name: crossprovider hermes scheduled-task-validation-must-exercise-the-actu
description: Scheduled task validation must exercise the actual scheduled mode, not just manual runs
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [testing, windows-tasks, acceptance-criteria]
---

MemoryBridgeSync plan gap: reviewing only manual one-off execution misses the real risk surface (--commit mode, rebase/push behavior). Task Scheduler evidence (registration state, last run, persistence across reboot) must be part of acceptance criteria, not left open.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
