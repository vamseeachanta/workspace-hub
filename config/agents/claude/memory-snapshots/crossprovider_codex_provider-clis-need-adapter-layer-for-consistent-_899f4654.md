---
name: crossprovider codex provider-clis-need-adapter-layer-for-consistent-
description: Provider CLIs need adapter layer for consistent interface
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [architecture, abstraction, providers, maintenance]
---

Provider CLIs use incompatible argument syntax (claude -p vs codex exec vs gemini -p -y). Wrap each in a consistent adapter (e.g., scripts/agents/providers/*.sh) to isolate CLI specifics from orchestration logic.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
