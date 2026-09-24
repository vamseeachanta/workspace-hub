---
name: crossprovider gemini scheduled-tasks-registry-schema-and-capability-d
description: Scheduled tasks registry schema and capability declaration
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [scheduled-tasks, infrastructure-automation, capability-declaration]
---

All scheduled tasks must be registered in `config/scheduled-tasks/schedule-tasks.yaml` with fields: id, label, schedule (cron string), machines (list), requires (capability list), prefer (machine hint), command (shell), log, is_claude_task, description. Scripts requiring specific tools (e.g., jq) must declare them in `requires` rather than relying on implicit CLI flag parsing like `gh --jq`, which is ambiguous and platform-dependent.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
