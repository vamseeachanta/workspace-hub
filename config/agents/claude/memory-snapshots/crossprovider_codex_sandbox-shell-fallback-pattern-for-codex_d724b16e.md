---
name: crossprovider codex sandbox-shell-fallback-pattern-for-codex
description: Sandbox shell fallback pattern for Codex
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [codex, environment, tooling-fallback, sandbox]
---

Local shell commands in this environment fail with `bwrap: loopback: Failed RTM_NEWADDR: Operation not permitted`. Switch to GitHub connector API for repository inspection when shell execution is blocked. This provides a reliable fallback for read-only repo analysis.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
