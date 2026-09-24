---
name: crossprovider gemini context-checkpoint-at-70-budget-hard-stop-preven
description: Context checkpoint at 70% budget hard-stop prevents mid-session gate erasure
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [context-management, session-design, gates]
---

Mandatory new session when reaching 70% of context_budget_kb preserves gate instructions and must-fire rules that would be compacted away by harness summarization. Hard-stop triggers checkpoint prompt + resume flow.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
