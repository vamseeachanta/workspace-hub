---
name: crossprovider hermes local-only-contract-for-cron-scheduled-audit-tas
description: Local-only contract for cron-scheduled audit tasks
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [scheduled-tasks, automation-safety, github-integration, cron-isolation]
---

Weekly skill audits and similar maintenance tasks must not invoke `gh` CLI, make network calls, or post to GitHub directly from the cron path. GitHub payloads can be rendered as local Markdown for manual review, but automated posting risks spam and state mutation. Codify this constraint explicitly in docs.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
