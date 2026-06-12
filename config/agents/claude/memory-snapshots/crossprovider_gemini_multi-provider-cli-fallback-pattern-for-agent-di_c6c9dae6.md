---
name: crossprovider gemini multi-provider-cli-fallback-pattern-for-agent-di
description: Multi-provider CLI fallback pattern for agent dispatch
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [orchestration, multi-provider, resilience, routing]
---

For systems routing work to multiple AI providers (Claude/Codex/Gemini): implement health_check(assigned_provider) → if unavailable, fallback through ordered chain [assigned, claude, codex, gemini]. Prevents dispatch failures when provider CLIs are missing/unavailable. Validate health checks before sending work, not after.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
