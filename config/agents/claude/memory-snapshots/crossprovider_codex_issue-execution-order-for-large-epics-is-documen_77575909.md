---
name: crossprovider codex issue-execution-order-for-large-epics-is-documen
description: Issue execution order for large epics is documented in comments, not inferred from numbers
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [github-workflow, issue-dependencies, epic-planning]
---

When auditing what to work on next in a multi-issue epic like #725, check the parent/sibling issue comments for documented execution order (e.g., "do #718 first, then #720/#719, then #721/#722/#723"). Don't infer order from issue numbers or start with the first open item; follow the documented sequence to avoid blocking dependencies.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
