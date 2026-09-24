---
name: crossprovider codex parallel-multi-agent-work-must-preserve-and-docu
description: Parallel multi-agent work must preserve and document unrelated file changes
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [workflow, multi-agent-execution, governance]
---

When multiple agents execute work in the same repository simultaneously, unrelated file changes created by sibling agents must not be reverted. Document these side effects explicitly in the active WRK under 'Out-of-Scope Side Effects'. This rule is codified in AGENTS.md and workflow-gatepass skill to persist across parallel sessions.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
