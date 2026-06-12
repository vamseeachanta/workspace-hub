---
name: crossprovider hermes hermes-cross-machine-sync-transferable-vs-machin
description: Hermes cross-machine sync: transferable vs machine-specific boundary
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [hermes-infrastructure, cross-machine-sync, ace-ecosystem]
---

Hermes config split: transferable via repo (skills/, SOUL.md, config.yaml) vs machine-specific (auth.json, .env, state.db, sessions/, memories/). Existing infrastructure: scripts/_core/sync-agent-configs.sh (JSON merge for Claude/Codex/Gemini), scripts/cron/harness-update.sh (daily update on ace-linux-1 only, not ace-linux-2 yet). To sync custom skills across machines: symlink ~/.hermes/skills → workspace-hub/.claude/plugins/hermes-skills/ or add harness-update to ace-linux-2 cron schedule. Do NOT copy .env or auth.json directly.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
