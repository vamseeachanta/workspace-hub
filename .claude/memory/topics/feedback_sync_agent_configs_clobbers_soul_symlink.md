> Git-tracked snapshot from Claude auto-memory. Captured: 2026-06-29
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_sync_agent_configs_clobbers_soul_symlink.md

---
name: feedback_sync_agent_configs_clobbers_soul_symlink
description: "nightly sync-agent-configs.sh copies the 4KB Hermes delta over ~/.hermes/SOUL.md, clobbering install-soul-runtime.sh's symlink — recurring gutted-identity drift (#2864)"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 125ef504-cd50-421e-a7c5-e585a8805650
---

`~/.hermes/SOUL.md` drift is RECURRING, not one-time. Root cause (verified 2026-05-28): two mechanisms fight nightly.

**Why:** `scripts/agents/install-soul-runtime.sh` symlinks `~/.hermes/SOUL.md` → `config/agents/hermes/SOUL.runtime.md` (19KB, full SHARED_SOUL identity+gates). But `scripts/_core/sync-agent-configs.sh` (L47 `HERMES_SOUL_TEMPLATE=config/agents/hermes/SOUL.md` — the 4KB DELTA source, NOT the runtime; L1249 `sync_hermes_plain_file`), invoked by `scripts/cron/harness-update.sh:346` on the **01:15 daily cron**, does `cmp -s` then `cp`+`mv -f` over the target — replacing the symlink with a 4KB plain copy of the wrong file. So Hermes loads a gutted identity, and any `install-soul-runtime.sh` fix survives <24h. Telltale: repeated `~/.hermes/SOUL.md.pre-install-backup.*` files all exactly 4061 bytes, mtimes ~01:16-01:18.

**How to apply:** when you see "SOUL.md is a COPY not symlink" / "DIFFERS from canonical" on a Hermes box, don't just re-run install-soul-runtime.sh (temporary) — the durable fix is in sync-agent-configs.sh (point template at SOUL.runtime.md AND/OR make it symlink-aware/skip). Tracked as [[project_orchestrator_consistency_decisions]] #2864. The same `cp`+`mv -f`-over-symlink pattern may clobber other synced agent files (Codex/Gemini) — audit the general class. Verify recurring-vs-one-time drift by listing the `.pre-install-backup.*` timestamps before assuming a single fix holds.
