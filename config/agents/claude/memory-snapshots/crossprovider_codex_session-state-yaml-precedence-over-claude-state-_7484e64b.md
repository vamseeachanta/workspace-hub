---
name: crossprovider codex session-state-yaml-precedence-over-claude-state-
description: Session state YAML precedence over .claude/state/ markers
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [work-queue, session-state, state-hierarchy]
---

Work queue orchestrators maintain an internal session state (YAML) that overrides `.claude/state/active-wrk` markers. Forced activation requires patching the session-level `active_wrk` field, not just writing to filesystem. State store takes precedence.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
