---
name: crossprovider gemini timeout-foreground-required-for-signal-propagati
description: Timeout --foreground required for signal propagation in subshells
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [bash-reliability, signal-handling, ci-cd]
---

Use `timeout --foreground` (never bare `timeout`) when invoking commands in subshells or via bash -c; without --foreground flag, timeout cannot reliably deliver SIGTERM/SIGKILL to child processes. Critical for CI/CD where signal handling gates cleanup.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
