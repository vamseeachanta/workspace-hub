---
name: crossprovider codex codex-sandbox-execution-blocker-bwrap-namespace-
description: Codex sandbox execution blocker: bwrap namespace errors
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [codex, environment, operational-hazard]
---

Codex execution environment can fail entirely with `bwrap: loopback: Failed RTM_NEWADDR` errors that block all shell commands, including simple `git status` and `true`. Observed in session 3 on 2026-05-21; requires fallback to Hermes/main-session runtime when shell access is needed for pre-completion audits or repo work.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
