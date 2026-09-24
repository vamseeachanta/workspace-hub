---
name: crossprovider codex text-based-workflow-instructions-fail-without-te
description: Text-based workflow instructions fail without technical enforcement gates
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [agent-behavior, workflow-enforcement, governance]
---

Agent compliance drops to 4% when backed by text alone (CLAUDE.md, AGENTS.md). LLMs optimize for task completion, not process adherence. Technical gates (pre-commit hooks, CI checks, approval markers, agent prefill) are required to reach >80% compliance across all agents.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
