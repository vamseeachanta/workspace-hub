---
name: crossprovider codex harness-change-detection-must-precede-no-tier-1-
description: Harness-change detection must precede 'no tier-1 changes' early exit in pre-push hooks
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [integration-patterns, pre-commit-hooks, control-flow]
---

When a pre-push hook needs to run on harness-only changes (root AGENTS.md, CLAUDE.md), the harness-detection logic must execute before any early-exit check that says 'no tier-1 repo changes detected'. Otherwise, a push that changes only harness files will exit before the harness check runs. Discovered in WRK-1094: pre-push.sh exited at line 118 when only root harness files changed, so the config-drift check at line 204 never executed.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
