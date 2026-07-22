> Git-tracked snapshot from Claude auto-memory. Captured: 2026-07-22
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_hermes_no_openrouter_always_gpt55.md

---
name: feedback-hermes-no-openrouter-always-gpt55
description: "User directive 2026-05-25 — Hermes must NOT use OpenRouter at all (key removed from ~/.hermes/.env) and must use gpt-5.5/openai-codex for ALL model routing (default, delegation, every quick_command, smart_routing cheap_model, all auxiliary.* tasks). Supersedes the Copilot-multiplier routing table in ai-orchestration.md."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: e9bcfa5b-c1dc-4596-834b-bda6539efc25
---

User directive given 2026-05-25, after a Hermes-health review found recurring
OpenRouter `402 requires more credits` errors (23 hits May 25, 02:25→07:18) on
`agent.context_compressor`, `tools.skills_tool`, and `agent.tool_executor`.

**Directive (verbatim intent):**
1. "Do not use openrouter at all. remove from settings."
2. "Always use gpt-5.5."

**Why:** the OpenRouter key was being pulled in indirectly — `config.yaml` had no
explicit `openrouter` provider, but every `auxiliary.*` task used `provider: auto`,
and `auto` resolved to OpenRouter because `OPENROUTER_API_KEY` was present in
`~/.hermes/.env`. The OpenRouter key's spend cap was so low ("can only afford 841
tokens") it 402'd constantly, degrading context compression and any auto-routed
tool/skill call. Main execution never broke because it runs on `gpt-5.5` via
`openai-codex` (OAuth, separate budget) — see [[feedback_hermes_provider_openai_codex_routes_via_codex_exec]].

**What was changed (2026-05-25, verified):**
- Removed `OPENROUTER_API_KEY` line from `~/.hermes/.env` (backup `.env.bak.20260525T103014`).
- Via `hermes config set` (file-safe vs hand-editing under a live gateway): set
  `delegation.model`, all 6 `quick_commands.*.model`, `smart_model_routing.cheap_model.model`,
  and every `auxiliary.*.model` (vision, web_extract, compression, session_search,
  skills_hub, approval, mcp, title_generation, curator, flush_memories) → `gpt-5.5`;
  set their `.provider` → `openai-codex`. Eliminated ALL `provider: auto`.
  Config backup `config.yaml.bak.20260525T103014`.
- Restarted the gateway (was an unsupervised user-level detached `gateway run --replace`,
  PID 1703026 → 1878521) so the live process drops the OpenRouter env var. New gateway
  is parented to `systemd --user` (PID 2651), telegram reconnected, `active_agents:0`.

**How to apply:**
- **Never re-introduce OpenRouter** in Hermes (no `OPENROUTER_API_KEY`, no `openrouter`
  provider, no route that resolves to it). If a task needs a cheap/aux model, use
  `gpt-5.5`/`openai-codex`, not OpenRouter.
- **Default every new Hermes model setting to `gpt-5.5`/`openai-codex`.** Do not add
  `gpt-5.4`, `gpt-5.4-mini`, `gpt-5.2`, gemini, copilot, or anthropic routes to the
  Hermes config without explicit user say-so. Avoid `provider: auto` (it can silently
  re-select a keyed provider).
- The historical Copilot-multiplier routing table in [[ai-orchestration]] (2026-04-08)
  is SUPERSEDED by this directive — don't restore it.

**Known capability caveat:** `auxiliary.vision` is now pinned to `gpt-5.5`/`openai-codex`.
If image analysis breaks, the codex backend may not accept image input — flag to user
and revert just that one block (don't re-enable OpenRouter to fix it).

**Restart method note:** the user-level gateway is NOT a systemd service (`gateway
restart`/`start` without `--system` route to the system service and demand sudo). The
working relaunch is `setsid env HERMES_ACCEPT_HOOKS=1 <venv>/bin/hermes gateway run
--replace </dev/null >log 2>&1 &` — `--replace` + `gateway.lock` cleanly takes over the
old PID; `</dev/null` avoids the codex/hermes stdin-detect hang. `Linger=no`, so it dies
on full logout but the daily update cron relaunches it.

Related: [[feedback_hermes_provider_openai_codex_routes_via_codex_exec]],
[[project_hermes_installation]], [[project_dispatch_provider_capacity]], [[ai-orchestration]].
