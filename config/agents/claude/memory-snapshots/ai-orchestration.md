---
name: AI orchestration — models, agents, and cross-review
description: Model routing, provider constraints, quota management, cross-AI review patterns, and Hermes config.yaml mapping
type: reference
---

## Copilot Provider Model Constraints (verified 2026-04-08)
GitHub Copilot API (`api.githubcopilot.com`) only proxies a fixed set of models:
- **GPT**: gpt-5.4, gpt-5.4-mini, gpt-5-mini, gpt-5.3-codex, gpt-5.2-codex, gpt-4.1, gpt-4o, gpt-4o-mini
- **Claude**: claude-opus-4.6, claude-sonnet-4.6, claude-sonnet-4.5, claude-haiku-4.5
- **Gemini**: gemini-2.5-pro ONLY (no flash/flash-lite)
- **Other**: grok-code-fast-1

**Known gotcha:** `gemini-2.5-flash` returns HTTP 400 "model_not_supported" through Copilot. Must route to `gemini` provider (Google AI Studio direct) instead. Fixed in `~/.hermes/config.yaml` on 2026-04-08.

## Hermes config.yaml Model Routing (2026-04-08)
| Config key | Model | Provider | Cost source |
|---|---|---|---|
| model.default | claude-opus-4.6 | anthropic | Claude Max |
| smart_routing.cheap_model | gemini-2.5-flash | gemini | Gemini Pro $19.99/mo |
| delegation | claude-sonnet-4.6 | anthropic | Claude Max |
| quick_commands.research | gemini-2.5-pro | copilot | Copilot flat-rate |
| quick_commands.code | claude-opus-4.6 | anthropic | Claude Max |
| quick_commands.review | gpt-5.4 | openai-codex | OpenAI $20/mo |
| quick_commands.quick | gemini-2.5-flash | gemini | Gemini Pro $19.99/mo |
| quick_commands.data | gemini-2.5-pro | copilot | Copilot flat-rate |
| quick_commands.batch | claude-sonnet-4.6 | copilot | Copilot flat-rate |

**Why:** Copilot as a multiplier — access GPT/Claude/Gemini-Pro at flat rate. Direct Gemini only for models Copilot can't proxy. Delegation through anthropic to preserve Copilot rate limits for unique models.

## Codex Quota Fallback (user preference)
- When Codex quota is exhausted, substitute **Claude Opus (claude-opus-4-6)** as the Codex cross-reviewer
- Note the substitution in evidence output

## Model Cost & Routing
- **Opus 4.6**: $5/$25/M tokens, ~5x verbosity, HIGH quota risk — use for complex architecture and 1M-context analysis only
- **Sonnet 4.6**: $3/$15/M tokens, concise — default for most work. Early access users preferred Sonnet 4.6 over Opus 4.5
- **Sonnet-only quota is the real binding constraint** — separate from all-models weekly cap, hits 100% first

## Quota Monitoring
- OAuth API: `GET https://api.anthropic.com/api/oauth/usage` with Bearer token + `anthropic-beta: oauth-2025-04-20`
- Returns: `seven_day.utilization`, `seven_day_sonnet.utilization`, `five_hour.utilization`, `resets_at`
- Token from `~/.claude/.credentials.json` → `.claudeAiOauth.accessToken`

## Cross-AI Review
- **Codex**: NOT on dev-primary (ace-linux-1); run via SSH to ace-linux-2
- **Gemini**: `echo content | gemini -p "prompt" -y` (non-interactive)
- **Codex for coding**: user preference to use Codex as implementation agent too, not just reviewer
- **Cross-review policy** (#1515, 2026-03-31): Claude=orchestrator, Codex=default adversarial reviewer, Gemini=optional third. Two-provider default. See `project_cross_review_policy.md` for enforcement gap details.

## Design Principles (durable)
- **Orchestrator context is working memory** — never wipe it. Subagents are ephemeral.
- **Delegate down**: if a subagent can do it, spawn it — don't burn orchestrator context
- **Domain modules are the moat**: routing layer is commodity — migrate freely, protect domain logic

## CLI vs MCP Token Cost (2026-03-29)
- CLI tools use significantly fewer tokens than MCP server equivalents — Playwright CLI uses ~90K fewer tokens than MCP browser automation
- CLIs have no server overhead, no process management, direct terminal integration
- **How to apply:** When both a CLI and MCP option exist for a tool, prefer the CLI path for token efficiency.

## Local AI Infrastructure (future)
- QMD + lightweight GPU = viable personal AI infra (tip from a friend, not yet verified)
- QMD = OpenClaw's per-agent persistent memory store (key-value, per workspace)
