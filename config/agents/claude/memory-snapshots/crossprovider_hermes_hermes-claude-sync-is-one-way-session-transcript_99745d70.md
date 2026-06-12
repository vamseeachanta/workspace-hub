---
name: crossprovider hermes hermes-claude-sync-is-one-way-session-transcript
description: Hermes→Claude sync is one-way; session transcripts and learnings stay machine-local
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [cross-agent-sync, memory-flow, portability-gap]
---

4 layers of Hermes feedback: (1) live memories (~/.hermes/) = machine-local, (2) session transcripts (124 MB) = machine-local, (3) .claude/skills/ = git-tracked/portable, (4) hermes-insights.yaml exports = git-tracked. Only distilled insights (YAML) travel via git. Claude learnings don't flow back to Hermes. Full session history and live memories never leave machine.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
