---
name: crossprovider codex transactional-cron-tooling-diverges-from-legacy-
description: Transactional cron tooling diverges from legacy installer on machine identity and variable expansion
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [cron, machine-identity, divergence, workspace-hub#3057]
---

cron_apply.py resolves live hosts to canonical registry keys (e.g., dev-primary), but catalog tasks are pinned to hostnames (ace-linux-1), causing mismatches. setup-cron.sh, cron_apply.py, and cron-audit.py each have separate implementations of environment variable expansion ($WORKSPACE_HUB, $LOG), none of which expand in the transactional path. Unify via shared renderer module with alias resolution and machine-aware placeholder expansion.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
