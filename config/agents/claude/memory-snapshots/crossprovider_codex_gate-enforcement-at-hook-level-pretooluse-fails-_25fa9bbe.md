---
name: crossprovider codex gate-enforcement-at-hook-level-pretooluse-fails-
description: Gate enforcement at hook level (PreToolUse) fails open for bash and subprocess paths
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [gate-design, hook-limitations, enforcement-architecture]
---

PreToolUse hooks intercept only Claude Write tool calls. Bash subprocess execution and direct file writes bypass hooks entirely. Real gate enforcement needs canonical entrypoint guards in bash scripts, with hooks as secondary defense. Single-layer enforcement = fail-open vulnerability.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
