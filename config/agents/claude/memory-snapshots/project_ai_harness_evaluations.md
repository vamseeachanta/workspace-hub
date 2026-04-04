---
name: AI harness evaluation initiative
description: Evaluation of complementary AI agent tools — GStack, Hermes, Paperclip, Superpowers audit, harness-update cron (#1466-1470), with #1545 as follow-on umbrella
type: project
---

Five evaluation tracks dispatched 2026-03-28:

- **#1466** — GStack (Gary Tan): complementary harness to GSD
- **#1467** — Hermes Agent (Nous Research): self-improving skill loop. **Decision: EXTRACT** — port the self-improving skill pattern into existing GSD/Superpowers stack, don't adopt Hermes wholesale.
- **#1468** — Paperclip: zero-human company orchestrator (low priority, research only)
- **#1469** — Superpowers plugin audit: verify version currency and update cadence
- **#1470** — Harness-update cron job (high priority): daily updates at 01:15 UTC for AI harness tools. Live in `scripts/cron/harness-update.sh`.

**Follow-on:** #1545 (opened ~2026-03-31) is the umbrella issue for agentic feature progression under GSD. Hermes is one candidate sidecar under that umbrella, not the only path. #1546 is Phase 0 enabler (machine targeting in work-item template).

**Why:** Scouting complementary tools ensures the harness stays competitive. #1467 concluded Hermes has useful patterns (auto-skill creation, messaging gateway) but shouldn't replace the GSD control plane.

**How to apply:** When suggesting tooling changes, check #1545 phases. Hermes installation state is in `project_hermes_installation.md`.
