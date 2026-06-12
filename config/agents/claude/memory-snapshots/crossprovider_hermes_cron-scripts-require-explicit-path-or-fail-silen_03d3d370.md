---
name: crossprovider hermes cron-scripts-require-explicit-path-or-fail-silen
description: Cron scripts require explicit PATH or fail silently
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [cron, environment, gotcha]
---

Cron environment lacks typical interactive shell PATH; scripts must set PATH=... explicitly or invoked tools fail with "not found" in cron context but work fine interactively. Affects any script installing/using tools like python, git, or custom binaries.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
