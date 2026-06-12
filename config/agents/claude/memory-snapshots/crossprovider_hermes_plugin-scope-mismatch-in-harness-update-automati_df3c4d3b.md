---
name: crossprovider hermes plugin-scope-mismatch-in-harness-update-automati
description: Plugin scope mismatch in harness-update automation
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [claude-plugins, automation, scope-detection, harness-update]
---

Harness updater checks all plugins at user scope only, marking project-scoped plugins as 'not found' and 'failed' even though they're available locally. Root cause: updater doesn't detect scope from `claude plugin list --json`. Affects plugin sync health reporting across agent sessions.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
