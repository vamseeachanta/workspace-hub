---
name: crossprovider gemini scheduled-automation-requires-registration-in-ca
description: Scheduled automation requires registration in canonical config/scheduled-tasks/schedule-tasks.yaml
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [infrastructure, automation, configuration-management]
---

All periodic tasks must register in the central YAML registry with schema: id, label, schedule (cron), machines, requires, prefer, command, log, is_claude_task, description. This registry serves as the authoritative task inventory for cron scheduling and documentation.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
