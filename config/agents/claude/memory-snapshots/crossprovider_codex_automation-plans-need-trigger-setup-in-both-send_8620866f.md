---
name: crossprovider codex automation-plans-need-trigger-setup-in-both-send
description: Automation plans need trigger setup in both sender and receiver
metadata:
  type: reference
  source: codex
  bridged: 2026-05-27
  tags: [github-automation, workflow-design, plan-review]
---

Plans adding `repository_dispatch` calls but omitting the `repository_dispatch:` trigger in the receiver workflow are unexecutable. Safe: automation plan diffs must show both the sender code and the updated workflow YAML triggers.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
