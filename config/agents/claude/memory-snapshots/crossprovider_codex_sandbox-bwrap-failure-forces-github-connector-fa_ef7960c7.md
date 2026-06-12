---
name: crossprovider codex sandbox-bwrap-failure-forces-github-connector-fa
description: Sandbox bwrap failure forces GitHub connector fallback in isolated Codex environments
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [sandbox-quirks, codex-environment, fallback-strategy]
---

Codex sandbox initialization can fail with `bwrap: loopback: Failed RTM_NEWADDR: Operation not permitted`, blocking all local shell execution before any command runs. Workaround: pivot to GitHub connector (gh CLI, public web inspection) for read-only analysis. Full read-write tasks remain blocked until shell access restored.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
