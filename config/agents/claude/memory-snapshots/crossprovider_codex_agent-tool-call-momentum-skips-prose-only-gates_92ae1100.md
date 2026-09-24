---
name: crossprovider codex agent-tool-call-momentum-skips-prose-only-gates
description: Agent tool-call momentum skips prose-only gates
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [workflow-gates, agent-behavior, executable-contracts]
---

Gate logic defined only as policy text or soft recommendations gets skipped because agent tool chains naturally continue without explicit executable stop conditions. Gate enforcement must live at entry-point code (e.g., `scripts/agents/plan.sh`), not prose.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
