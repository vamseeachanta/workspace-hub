---
name: crossprovider codex multi-machine-consistency-via-role-tagged-declar
description: Multi-machine consistency via role-tagged declarative infrastructure
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [multi-machine, infrastructure, workspace-hub, architecture]
---

Two machines with divergent local state (crontab, ~/.claude/settings.json, mounts) but identical git-tracked harness create silent drift. Pattern: promote local config into git as role-tagged manifest (control-plane vs comms-dispatch vs sim-worker) + idempotent reconciler (bootstrap-machine.sh). Allows role-specific drift self-healing. PREREQUISITE: fix observability first (silent cron failures prevent detection).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
