---
name: crossprovider codex approval-gates-must-require-same-round-active-pr
description: Approval gates must require same-round active-provider consensus, not just patches
metadata:
  type: reference
  source: codex
  bridged: 2026-07-01
  tags: [process, review-gates, approval-semantics]
---

A plan cannot transition from draft to review without fresh same-round reviews showing no MAJOR findings from all available active providers. When a provider is unavailable (e.g., Gemini), consensus must come from the remaining set. Patching prose alone or having historical MAJOR verdicts from prior rounds is insufficient; approval requires explicit new evidence.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
