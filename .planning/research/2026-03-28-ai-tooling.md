# Research: ai-tooling — 2026-03-28

## Key Findings

1. **Claude Code v2.1.76 — Voice mode, 1M token context, Opus 4.6 default.** March brought push-to-talk voice mode (`/voice`), a 1M token context window, lazy-loading MCP tool search, transcript search, and richer hook events. VS Code extension entered beta. ([Releases](https://github.com/anthropics/claude-code/releases) · [Changelog](https://code.claude.com/docs/en/changelog) · [March roundup](https://pasqualepillitteri.it/en/news/381/claude-code-march-2026-updates))

2. **Claude Code SDK renamed to Claude Agent SDK (v0.2.85).** Breaking change: default system prompt removed, filesystem settings no longer auto-loaded, `ClaudeCodeOptions` → `ClaudeAgentOptions`. Session forking and programmatic inline subagents now supported. ([Migration guide](https://platform.claude.com/docs/en/agent-sdk/migration-guide) · [npm](https://www.npmjs.com/package/@anthropic-ai/claude-agent-sdk) · [Python releases](https://github.com/anthropics/claude-agent-sdk-python/releases))

3. **GSD v1.25 / GSD-2 — TypeScript rewrite, 32K+ stars.** GSD-2 is a standalone TypeScript process that manages git branches, cost tracking, stuck-loop detection, crash recovery, and autonomous milestone execution. 30+ new skill packs, 8-question quality gates added. ([GSD repo](https://github.com/gsd-build/get-shit-done) · [GSD-2 repo](https://github.com/gsd-build/gsd-2) · [Coverage](https://aiforautomation.io/news/2026-03-18-gsd-get-shit-done-claude-code-meta-prompting-32k-stars))

4. **MCP v1.27 — Tasks primitive, streaming elicitation, enterprise roadmap.** The Tasks primitive (SEP-1686) adds call-now/fetch-later for long-running agent work. MCP Server Cards (`.well-known` URLs) enable server discovery. Enterprise focus on audit trails, SSO auth, and config portability. ([2026 MCP Roadmap](http://blog.modelcontextprotocol.io/posts/2026-mcp-roadmap/) · [v1.27 analysis](https://www.contextstudios.ai/blog/mcp-ecosystem-in-2026-what-the-v127-release-actually-tells-us) · [New Stack coverage](https://thenewstack.io/model-context-protocol-roadmap-2026/))

5. **Codex CLI rebuilt around agentic workflows; Gemini CLI v0.35.2 with subagents-by-default.** Codex now supports image attachments, plugins as first-class, and structured inter-agent messaging via path-based addresses. Gemini CLI ships Linux-native sandboxing (bubblewrap + seccomp), model-driven parallel tool scheduler, and subagent JIT context injection. Free-tier Gemini Pro access ended March 25. ([Codex changelog](https://developers.openai.com/codex/changelog) · [Gemini CLI releases](https://github.com/google-gemini/gemini-cli/releases) · [Gemini latest](https://geminicli.com/docs/changelogs/latest/))

## Relevance to Project

| Finding | Impact on Workspace Hub |
|---------|------------------------|
| **Claude Code 1M context + voice** | Voice mode could accelerate prompt dictation workflow (matches `user_voice_prompt_tips.md`). 1M context benefits the multi-repo orchestration sessions that currently hit context limits. |
| **Agent SDK rename** | If you build any programmatic agents via the SDK (e.g., nightly researchers from Phase 5), imports and options need updating. The `settingSources` opt-in means your `CLAUDE.md`/`.claude/` config won't load unless explicitly requested. |
| **GSD-2 TypeScript rewrite** | Your GSD skills inventory is extensive. GSD-2 adds autonomous milestone execution with crash recovery — directly relevant to Phase 5 (nightly research automation). Evaluate whether to migrate from v1.x skill-based GSD to GSD-2's process model. |
| **MCP Tasks primitive** | The call-now/fetch-later pattern aligns with your nightly researcher design. Long-running data pipeline monitoring (worldenergydata staleness checks) could use MCP Tasks instead of cron-based polling. |
| **Codex & Gemini subagent maturity** | Your multi-provider cross-review workflow (`Claude Code, Codex CLI, Gemini CLI`) benefits from all three CLIs now having first-class subagent support. Gemini's free-tier restriction means you'll need a paid subscription to keep using Gemini Pro for cross-review. |

## Recommended Actions

- [ ] **Check GSD version** — Run `/gsd:update` to see if you're on v1.25+; evaluate GSD-2 for Phase 5 nightly automation (create GitHub issue to track evaluation)
- [ ] **Gemini CLI paid tier** — Verify Gemini subscription status since free Pro access ended March 25; if using Gemini for cross-review, ensure paid plan is active (create GitHub issue)
- [ ] **Agent SDK migration** — If nightly researchers will use the Agent SDK programmatically, update imports per the [migration guide](https://platform.claude.com/docs/en/agent-sdk/migration-guide); add `settingSources` to preserve `.claude/` config loading (promote to Phase 5 plan)
- [ ] **MCP Tasks evaluation** — Assess MCP v1.27 Tasks primitive for long-running data pipeline monitoring in worldenergydata; could replace cron-based staleness checks (create GitHub issue for Phase 5 scope)
- [ ] **Voice mode trial** — Test `/voice` for prompt dictation; may replace the Linux keyboard shortcut workarounds documented in `user_voice_prompt_tips.md` (ignore if voice quality insufficient — low priority)
