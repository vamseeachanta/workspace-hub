---
name: crossprovider codex github-connector-enables-read-only-audits-when-l
description: GitHub connector enables read-only audits when local shell is blocked
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [fallback-pattern, sandbox-unavailability, connector-resilience]
---

When the local sandbox fails with loopback namespace errors (`bwrap: loopback: Failed RTM_NEWADDR`), the GitHub connector can still retrieve issue metadata, label state, file content, and commit evidence. This allows audit and report work to proceed without local filesystem access, though it cannot verify worktree state or run local commands.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
