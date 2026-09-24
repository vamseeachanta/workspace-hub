---
name: crossprovider codex shell-sandbox-failures-recoverable-via-github-co
description: Shell sandbox failures recoverable via GitHub connector fallback
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [shell-infrastructure, fallback-pattern, resilience]
---

When local command execution fails with `bwrap: loopback: Failed RTM_NEWADDR`, fallback to GitHub connector for repository evidence. Read-only governance audits proceed using API/connector sources without blocking work.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
