---
name: Hermes Agent installation state
description: Hermes v0.4.0 installed at ~/.hermes/ with venv deps and API keys configured — shebang reverts are a recurring issue
type: project
---

Hermes Agent v0.4.0 (Nous Research) is installed on dev-primary (ace-linux-1) as of 2026-03-28.

**Installation layout:**
- Agent code: `~/.hermes/hermes-agent/` (cloned from https://github.com/NousResearch/hermes-agent)
- Binary: `~/.local/bin/hermes`
- Venv: `~/.hermes/hermes-agent/.venv/` (created 2026-04-01 via `uv venv`)
- Dependencies installed via `uv pip install -e ".[all]"` into the venv
- State DB: `~/.hermes/state.db`, memory: `~/.hermes/memories/`, sessions: `~/.hermes/sessions/`
- Daily updates: `scripts/cron/harness-update.sh` runs `hermes update` at 01:15 UTC (#1470)

**API keys:** Configured in `~/.hermes/.env` (created 2026-04-04, 4 keys). No longer a blocker.

**Recurring issue — launcher shebang reverts:** The `~/.local/bin/hermes` shebang must be `#!/home/vamsee/.hermes/hermes-agent/.venv/bin/python` (not `#!/usr/bin/env python3`). It has reverted at least twice:
- 2026-04-01: Fixed during initial setup, later reverted (likely by `hermes update` or external edit)
- 2026-04-06: Fixed again after `ModuleNotFoundError: No module named 'dotenv'` crash

**Why this keeps happening:** `hermes update` or pip reinstall likely regenerates the launcher with a generic shebang. The venv Python is needed because `python-dotenv` and other deps are only in the venv, not the system/miniforge Python.

**Mitigation idea:** A post-update hook or wrapper script could pin the shebang after each `hermes update`.

**Governance:** #1545 is the umbrella issue for agentic feature progression under GSD. #1546 is the Phase 0 enabler (machine targeting in work-item template). Hermes is one candidate sidecar — GSD remains the control plane. Decision from #1467: EXTRACT useful patterns, don't adopt Hermes wholesale.

**How to apply:** If hermes crashes with `ModuleNotFoundError`, check the shebang first. Skills backfill from Hermes to repo `.claude/skills/` is in progress.
