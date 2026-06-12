---
name: crossprovider codex bare-python3-persists-despite-uv-migration-acros
description: Bare python3 persists despite uv migration across all providers
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [tooling-convention, provider-consistency, uv-migration]
---

All providers (Claude, Codex, Gemini, Hermes) still invoke bare `python3` frequently enough in planning and execution contexts to warrant systematic reinforcement toward `uv run ... python` convention in provider-facing guidance.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
