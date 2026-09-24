---
name: crossprovider gemini preserve-existing-infrastructure-ids-during-work
description: Preserve Existing Infrastructure IDs During Workflow Upgrades
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [workflow, operations, naming]
---

When upgrading or reimplementing scheduled tasks or orchestration workflows, preserve existing task IDs and infrastructure references (e.g., cron config keys) rather than creating new ones. Dual infrastructure creates orphaned state and confuses operational inventory.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
