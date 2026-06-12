---
name: crossprovider hermes dirty-main-branch-during-multi-agent-sessions-ob
description: Dirty main branch during multi-agent sessions obscures review targets
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [multi-agent, session-isolation, git-state]
---

Active overnight processes modify config files and session logs, making it hard to isolate changes relevant to a specific review target. Preflight must identify active process conflicts (e.g., #2348 worker running) to avoid false positives in adversarial reviews.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
