---
name: hermes-agent-installation-state
description: Hermes v0.13.0 installed at ~/.hermes/ on ace-linux-1; default routes through openai-codex/gpt-5.5; OpenAI Codex OAuth + OpenRouter/Gemini API keys configured; 5+ cron jobs active
metadata: 
  node_type: memory
  type: project
  originSessionId: 5ee013a1-b9cb-4061-a14e-9618d4d297ce
---

Hermes Agent **v0.13.0 (release 2026.5.7)** is installed on ace-linux-1, verified 2026-05-13. Upgrade from v0.4.0 → v0.13.0 landed in-place (same install path); `hermes update` self-check reports "Up to date".

**Installation layout (unchanged from v0.4):**
- Agent code: `~/.hermes/hermes-agent/` (cloned from https://github.com/NousResearch/hermes-agent)
- Venv binary: `~/.hermes/hermes-agent/.venv/bin/hermes` (this is the one to call — shebang `#!/home/vamsee/.hermes/hermes-agent/.venv/bin/python3`, last touched 2026-04-16)
- State DB: `~/.hermes/state.db`, auth: `~/.hermes/auth.json`, skills: `~/.hermes/skills/`
- Config: `~/.hermes/config.yaml`, secrets: `~/.hermes/.env`
- Daily updates: `scripts/cron/harness-update.sh` runs `hermes update` at 01:15 UTC (#1470)

**Default provider in v0.13.0:** `gpt-5.5` via `openai-codex` (changed from v0.4's `claude-sonnet-4.6` via `copilot`). Max turns: 90. Working dir defaults to `/mnt/local-analysis/workspace-hub`, timezone America/Chicago.

**Auth state (verified 2026-05-13):**
- OpenAI Codex OAuth: ✓ logged in (auth.json refreshed 2026-05-06)
- OpenRouter API key: ✓ set
- Google/Gemini API key: ✓ set
- Anthropic API key: ✗ not set (Anthropic traffic must route via Claude Code CLI, not Hermes-direct)
- Nous Portal OAuth: ✗ not logged in (new in v0.13; not required for current routing)

**Active cron jobs (5 confirmed via `hermes cron list`):**
- `deepseek-weekly-check` (Mon 09:00)
- `memory-bridge-daily` (04:00)
- `gmail-daily-digest` (12:00)
- `wiki-health-weekly` (Mon 10:00)
- `tier1-indexing-daily` (03:30)

**v0.13 surface changes worth knowing:**
- CLI noun `skill` → `skills` (plural). Scripts calling `hermes skill list` will fail with "invalid choice" — use `hermes skills`.
- New subcommands visible: `kanban`, `plugins`, `curator`, `profile`, `dashboard`, `claw`, `computer-use`, `acp`. The `kanban` surface backs #2665's quota dashboard work.
- New auth provider: Nous Portal (OAuth). Optional for current routing; required if pulling Nous-hosted models.
- `delegate_task` synchronous-subtask primitive is available per #2695 D7 design; empirical test pending in [#2702](https://github.com/vamseeachanta/workspace-hub/issues/2702) (the routing-audit residue from #2696). Note: `delegate_task` is a TOOL inside Hermes, **not a CLI subcommand** — `hermes delegate ...` will fail with "invalid choice: 'delegate'".

**Non-interactive prompt invocation (verified 2026-05-14, corrected 2026-05-15):** `hermes -z "$PROMPT" --yolo` is the Hermes equivalent of `claude -p` — runs the prompt through the configured provider (currently `openai-codex` / `gpt-5.5` per `hermes config show`), auto-confirms tool calls, exits with the response on stdout.

**HOWEVER — important correction (2026-05-15):** `hermes -z` routes Codex calls *through* the `codex exec` subprocess, NOT via Hermes's own direct OpenAI API connection. A small probe (30-byte prompt → "hello-from-hermes") returned exit 0 and gave the false impression that the CLI binary was bypassed; longer prompts that trigger Codex tool execution shell out to `codex exec` and inherit the 0.130.0 stdin-hang regression. Verified 2026-05-15 via traced process tree: `hermes wrapper → codex exec → hang`. 12 lingering hung processes accumulated during a #2548 Codex T1 review attempt before they were killed. **For larger Codex-routed work, the codex-cli stdin-hang IS still a hazard via the Hermes path.** Workarounds: (a) downgrade codex-cli to 0.123.0 per `feedback_codex_cli_0_124_upstream_regression`, (b) use Claude code-reviewer agent for review work where Codex independence isn't critical, (c) keep prompts small and accept short-probe-only validation.

**Claude `-p` mode hard limit:** `claude --dangerously-skip-permissions -p "$PROMPT"` rejects prompts >4000 characters with "Goal condition is limited to 4000 characters". Verified 2026-05-15 when a 5325-char #2702 dispatch prompt died at launch (PID 753189 was the wrapper, claude child never started). Compose dispatch prompts under 4000 chars or pipe via stdin/file. Hermes `-z` does NOT have this limit (overnight H-lanes ran with much larger prompts).

**Stale local launcher (low priority):** `~/.local/bin/hermes` shebang still points at `venv/bin/python3` (note: missing dot — predates the `.venv/` rename), last touched 2026-04-20. Direct invocation via `~/.hermes/hermes-agent/.venv/bin/hermes` (or `python -m hermes_cli.main`) bypasses it cleanly. Fix needed only if something calls `hermes` from PATH.

**Historical shebang-revert pattern (v0.4 era, retained for context):** Between 2026-04-01 and 2026-04-08 the venv launcher shebang reverted to `#!/usr/bin/env python3` at least three times after `hermes update` / pip reinstall, causing `ModuleNotFoundError: No module named 'dotenv'`. The v0.13 install has held the venv-pinned shebang stable since 2026-04-16. If `ModuleNotFoundError` returns, check the launcher shebang first.

**Governance:** [#1545](https://github.com/vamseeachanta/workspace-hub/issues/1545) umbrella for agentic feature progression; [#2519](https://github.com/vamseeachanta/workspace-hub/issues/2519) orchestrates AI provider usage; [#2696](https://github.com/vamseeachanta/workspace-hub/issues/2696) tracks the upgrade audit (binary-upgrade portion done; routing-layer empirical audit + Anthropic-base-vs-overage consumption verification still open). [#2695](https://github.com/vamseeachanta/workspace-hub/issues/2695) D7 brain/hands model assumes v0.13.0 capabilities — assumption is now grounded.

**How to apply:**
- Invoke via `~/.hermes/hermes-agent/.venv/bin/hermes` or `python -m hermes_cli.main` from that venv — not the stale `~/.local/bin/hermes`.
- If a script breaks with "invalid choice: 'skill'", swap to `skills`.
- Before treating "Hermes routes brain to Codex" as fact, verify via `hermes config show` → Model field, since defaults shifted between v0.4 and v0.13.
- For #2695 picklist routing (Hermes → Codex / Hermes → Claude Code), the auth currently supports the Codex hand (OAuth ✓); the Claude Code hand requires Claude Code CLI to be invokable on this machine (separate auth surface, not Hermes-internal).
