> Git-tracked snapshot from Claude auto-memory. Captured: 2026-04-05
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/ai-orchestration.md

---
name: AI orchestration — models, agents, and cross-review
description: Model routing, quota management, cross-AI review patterns, and agent preferences across the workspace ecosystem
type: reference
---

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
- **How to apply:** When both a CLI and MCP option exist for a tool, prefer the CLI path for token efficiency. Relevant to our context budget monitoring (35%/25% thresholds).

## GSD Framework Version
- Harness-update cron job (#1470) in progress to automate daily updates — verify current version via `node .claude/get-shit-done/bin/gsd-tools.cjs --version` if needed

## Local AI Infrastructure (future)
- QMD + lightweight GPU = viable personal AI infra (tip from a friend, not yet verified)
- QMD = OpenClaw's per-agent persistent memory store (key-value, per workspace)
