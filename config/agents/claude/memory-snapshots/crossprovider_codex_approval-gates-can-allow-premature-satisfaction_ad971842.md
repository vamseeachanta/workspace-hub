---
name: crossprovider codex approval-gates-can-allow-premature-satisfaction
description: Approval gates can allow premature satisfaction
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [approval-gates, scope, design]
---

Plans state mandatory requirements like 'fresh external rerun required' but acceptance criteria only check 'artifact exists', creating a loophole where user approval skips the stated step. Gate definitions must match stated requirements.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
