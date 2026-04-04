---
name: Hermes Agent installation state
description: Hermes v0.4.0 installed at ~/.hermes/ with venv deps, blocked on API key config — part of #1545 agentic progression
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

**Current blocker:** No API key configured. `~/.hermes/.env` does not exist. Hermes needs at least one of `OPENROUTER_API_KEY`, `OPENAI_API_KEY`, or `ANTHROPIC_API_KEY` to connect to an LLM provider. User was asked which provider to use but deferred the decision.

**Launcher note:** The `~/.local/bin/hermes` shebang was changed to point at the venv Python during the 2026-04-01 session, but was later reverted (externally or by linter) back to `#!/usr/bin/env python3`. The launcher may need the venv shebang restored or a PATH/activation wrapper for deps to resolve.

**Governance:** #1545 is the umbrella issue for agentic feature progression under GSD. #1546 is the Phase 0 enabler (expand work-item machine targeting). Hermes is one candidate sidecar — GSD remains the control plane. Decision from #1467: EXTRACT useful patterns, don't adopt Hermes wholesale.

**Why:** User is evaluating whether Hermes can perform work on repos (e.g., digitalmodel) as an agentic sidecar. Getting it to a runnable state is Phase 2 of #1545.

**How to apply:** Before using `hermes` CLI, verify the launcher shebang points to the venv Python (`~/.hermes/hermes-agent/.venv/bin/python3`) and that `~/.hermes/.env` has a valid API key.
