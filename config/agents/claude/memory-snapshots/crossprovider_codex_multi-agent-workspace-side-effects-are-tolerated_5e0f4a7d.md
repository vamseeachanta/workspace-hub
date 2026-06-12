---
name: crossprovider codex multi-agent-workspace-side-effects-are-tolerated
description: Multi-agent workspace side effects are tolerated, not reverted
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [workflow-paradigm, multi-agent-coordination, parallel-execution]
---

In parallel multi-agent work, unrelated file changes from concurrent agents are non-blocking and must not be reverted unless explicitly directed; document them in the active WRK under 'Out-of-Scope Side Effects'. This pattern was codified in canonical workflow docs to support true parallelism across providers (Claude, Codex, Gemini).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
