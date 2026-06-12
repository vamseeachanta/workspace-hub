---
name: crossprovider gemini gh-jq-availability-in-scheduled-tasks
description: gh --jq availability in scheduled tasks
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [tooling-quirk, scheduled-tasks, gh-cli]
---

`gh --jq` behavior is ambiguous in scheduled-task execution context; issue #2550 pattern requires explicit `jq` binary as a capability dependency in schedule-tasks.yaml to avoid silent failures. Do not assume gh provides its own jq.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
