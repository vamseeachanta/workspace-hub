---
name: crossprovider codex hard-gates-need-enforcement-hooks-not-just-scrip
description: Hard gates need enforcement hooks, not just scripts
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [gates, policy, workspace-hub-governance]
---

A hard-stop policy requires actual blocking (git hooks, CI gates, GitHub Actions intercepts), not a script that can be bypassed with env vars (e.g., COMPLETENESS_ALLOW=1). Scripts alone are bypassable and give false confidence. Enforcement must be in the automation layer, not user discretion.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
