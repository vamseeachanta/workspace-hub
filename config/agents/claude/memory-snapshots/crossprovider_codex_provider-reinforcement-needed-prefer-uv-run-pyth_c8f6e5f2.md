---
name: crossprovider codex provider-reinforcement-needed-prefer-uv-run-pyth
description: Provider reinforcement needed: prefer `uv run python` over bare `python3`
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [provider-guidance, tooling-consistency, environment-management]
---

Multiple providers (Hermes, Gemini, Codex) still invoke bare `python3` even when `uv` is available in the environment. Reinforce `uv run python` (or `uv run ... python`) in provider prompts and system guidance; the current reinforcement is not sticky enough across session boundaries.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
