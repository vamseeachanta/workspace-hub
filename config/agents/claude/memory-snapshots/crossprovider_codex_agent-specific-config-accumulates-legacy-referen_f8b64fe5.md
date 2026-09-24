---
name: crossprovider codex agent-specific-config-accumulates-legacy-referen
description: Agent-specific config accumulates legacy references
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [config-drift, multi-agent-coordination, validation]
---

Agent-specific config files (e.g., `.codex/CODEX.md`, `.codex/config.toml`) can retain outdated references (e.g., WRK-* work-queue patterns) that conflict with newer canonical workflows (e.g., GitHub issue planning in `AGENTS.md`). Cross-agent work should validate and update stale references in all agent configs.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
