Perfect. Now I'll update memory to track the latest AI tooling findings:

---

# Research: ai-tooling — 2026-04-01

## Key Findings

- **Claude Code v2.1.76+ — Voice mode, 1M context, computer use, Opus 4.6 64k→128k tokens.** March 2026 shipped push-to-talk voice mode (`/voice`, 20 languages), recurring tasks (`/loop 5m check`), extended 1M token context, and computer use (Pro/Max) for file operations and desktop control. VS Code extension entered beta. Output token limits increased: Opus 4.6 default 64k, max 128k for Opus/Sonnet. 

- **GSD v1.25+ — New researcher/debugger agents (915/990 lines), multi-runtime support (Codex, Gemini CLI).** March updates ship gsd-researcher (4 modes: ecosystem, feasibility, implementation, comparison) and gsd-debugger (7+ investigation techniques). Multi-runtime support via `npx get-shit-done-cc` for OpenCode/Gemini/Codex. `/gsd:fast` for trivial tasks, `/gsd:profile-user` developer profiling across 8 dimensions, `/gsd:plant-seed` for backlog with trigger conditions.

- **MCP v1.27+ — Tasks primitive (call-now/fetch-later), Server Cards discovery, enterprise auth/audit focus.** The Tasks primitive (SEP-1686) enables long-running agent work with deferred results. MCP Server Cards expose structured metadata via `.well-known` URLs for discovery. Enterprise focus: SSO auth, gateway/proxy patterns, config portability, audit trails, and observability. TypeScript SDK 1.27.0/1.27.1 adds auth conformance and OAuth server discovery. 34.7k dependent projects on npm.

- **Agent SDK (Anthropic) v0.2.87 (TS), v0.1.48 (Python) — taskBudget token awareness, agentProgressSummaries, seed_read_state.** TypeScript: fixed `@anthropic-ai/sdk` dependencies, added `reloadPlugins()` for hot-reload. Python: fixed type:'sdk' MCP servers via `--mcp-config`. Both: taskBudget for API-side pacing, progress summaries with task_progress events, and seed_read_state for Edit context after Read removal.

- **Codex CLI + Gemini CLI — Agentic workflows matured; multi-agent orchestration frameworks proliferating.** Codex now supports image attachments, plugins as first-class (sync at startup), subagent path-based addresses (`/root/agent_a`), and GPT-5.3-Codex with 25% faster inference. Gemini CLI v0.35.3+ has subagents enabled by default with model-driven parallel tool scheduler and JIT context injection. Third-party orchestrators (Ruflo, Claude Flow, oh-my-claudecode) provide enterprise-grade multi-agent frameworks; Claude's built-in Agent Teams coordinates work via shared task lists.

## Relevance to Project

| Finding | Affected Workflow / Package |
|---------|---------------------------|
| **Claude Code voice + computer use** | `user_voice_prompt_tips.md` — voice mode (`/voice`) obsoletes Linux keyboard shortcuts for voice dictation. Computer use enables automation of licensed machine tasks without manual intervention. |
| **GSD researcher/debugger agents + multi-runtime** | Phase 5 (nightly research automation) can leverage gsd-researcher's 4-mode methodology and multi-runtime support to spawn Codex/Gemini researchers in parallel. Phase 7 (solver verification) can use gsd-debugger for systematic OrcFxAPI troubleshooting. |
| **MCP Tasks primitive** | `worldenergydata` staleness checks (Phase 2) currently use cron. MCP Tasks enable call-now/fetch-later for long-running pipeline monitoring without polling. Aligns with Phase 5 research automation. |
| **Agent SDK taskBudget + progress summaries** | If Phase 5 nightly researchers build on Agent SDK, taskBudget controls cost runaway, and agentProgressSummaries enable real-time monitoring of long-running background agents. |
| **Codex/Gemini multi-agent + Agent Teams** | Cross-review workflow (Claude Code, Codex CLI, Gemini CLI per PROJECT.md) can now coordinate at scale via Agent Teams or third-party orchestrators. Codex plugins-first model aligns with GSD skill packs. |
| **GSD `/gsd:profile-user`** | Captures developer behavioral profile across 8 dimensions. Could feed into nightly researcher configuration (Phase 5) to adapt research style to user preferences. |

## Recommended Actions

- [ ] **Trial:** Test Claude Code `/voice` for prompt dictation; if quality sufficient, deprecate Linux keyboard shortcuts in `user_voice_prompt_tips.md` and update with voice mode flow
- [ ] **Create GitHub issue:** Evaluate MCP v1.27 Tasks primitive for worldenergydata staleness checks; refactor from cron-based polling to call-now/fetch-later pattern (Phase 2 technical debt)
- [ ] **Create GitHub issue:** Assess GSD-2 candidate architecture for Phase 5 nightly research automation vs. Phase 5 current plan; if GSD-2 process model offers crash recovery + autonomous milestone execution, evaluate migration lift
- [ ] **Promote to PROJECT.md:** Add note under Workflow section: "Agent Teams + Codex/Gemini subagents enable multi-runtime orchestration for cross-review (Claude/Codex/Gemini); evaluate third-party orchestrators (Ruflo, Claude Flow) for production multi-agent sprints"
- [ ] **Promote to PROJECT.md:** Update AI agents entry: "Claude Code v2.1.76+, Codex CLI (plugins-first, GPT-5.3), Gemini CLI v0.35.3+ (subagents default) — see multi-agent orchestration note"
- [ ] **Monitor:** GSD v1.26+ releases for any Phase 5 nightly researcher pattern refinements; currently tracking v1.25 researcher agent as foundation
- [ ] **Monitor:** MCP Server Card adoption — when first production registries appear, evaluate registering workspace-hub as discoverable MCP source
- [ ] **Ignore (low priority):** Claude Code recurring tasks (`/loop`) — useful for periodic checks but not critical to current Phase 7 verification gate scope

---

Sources:
- [Claude Code releases](https://github.com/anthropics/claude-code/releases)
- [Claude Code changelog](https://code.claude.com/docs/en/changelog)
- [Claude Code March 2026 updates](https://pasqualepillitteri.it/en/news/381/claude-code-march-2026-updates)
- [GSD releases](https://github.com/gsd-build/get-shit-done/releases)
- [GSD CHANGELOG](https://github.com/gsd-build/get-shit-done/blob/main/CHANGELOG.md)
- [MCP 2026 roadmap](http://blog.modelcontextprotocol.io/posts/2026-mcp-roadmap/)
- [MCP ecosystem in 2026 analysis](https://www.contextstudios.ai/blog/mcp-ecosystem-in-2026-what-the-v127-release-actually-tells-us)
- [MCP roadmap coverage](https://thenewstack.io/model-context-protocol-roadmap-2026/)
- [Agent SDK TypeScript releases](https://github.com/anthropics/claude-agent-sdk-typescript/releases)
- [Agent SDK TypeScript CHANGELOG](https://github.com/anthropics/claude-agent-sdk-typescript/blob/main/CHANGELOG.md)
- [Codex CLI documentation](https://developers.openai.com/codex/cli)
- [Gemini CLI releases](https://github.com/google-gemini/gemini-cli/releases)
- [Shipyard multi-agent orchestration](https://shipyard.build/blog/claude-code-multi-agent/)
- [Ruflo orchestration platform](https://github.com/ruvnet/ruflo)
- [Claude Code Agent Teams documentation](https://code.claude.com/docs/en/agent-teams)
