---
name: Nightly GSD researchers — live and producing output
description: Domain-rotating research agents running nightly via cron — outputs to .planning/research/, integrated into /today morning
type: project
---

Nightly GSD researchers are **live and running** as of 2026-03-27.

**Schedule (day-of-week rotation):**
- Monday = standards (API, DNV, ABS, ISO)
- Tuesday = python-ecosystem (uv, deps, CVEs)
- Wednesday = ai-tooling (Claude CLI, GSD, MCP)
- Thursday = competitor-market (SESAM, SACS, OrcaFlex)
- Friday = synthesis (week review + ranked actions)
- Saturday/Sunday = off

**Implementation:**
- Script: `scripts/cron/gsd-researcher-nightly.sh` (runs at 1:35 AM on dev-primary)
- Design spec: `docs/superpowers/specs/2026-03-25-nightly-gsd-researcher-design.md` (#1434)
- Output: `.planning/research/YYYY-MM-DD-<domain>.md`
- Morning integration: `scripts/productivity/sections/research-highlights.sh` surfaces findings in `/today`
- Staleness check: 6:00 AM cron alerts if no research in 60h

**Why:** PROJECT.md was hand-written for brownfield setup. Researchers discover new patterns, dependencies, and ecosystem changes over time that the hand-written version misses.

**How to apply:** Research outputs accumulate in `.planning/research/`. Wednesday's ai-tooling slot is a natural feed for new Claude Code feature discovery (relevant to the planned workflow-tips catalog).
