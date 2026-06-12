---
name: crossprovider hermes windows-machine-gui-verification-gate-for-execut
description: Windows machine GUI verification gate for execution readiness
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [windows, machines, readiness, verification-gate, blocker, execution-lane]
---

Windows machine placement and execution-readiness issues (#2772, #2773 pattern) cannot close or move to implementation until live GUI screenshots validate: checkout paths, git/provider/auth state, solver/license state, Task Scheduler readiness. Terminal commands, file listings, and registry queries are insufficient evidence. This requirement is specific to Windows machines where programmatic state verification is unreliable.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
