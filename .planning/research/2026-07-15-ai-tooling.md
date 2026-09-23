# Research: ai-tooling — 2026-07-15

## Key Findings

1. **Anthropic Agent SDK multi-agent orchestration entered public beta (May 6, 2026).** Lead agent breaks work into pieces, delegates to specialist sub-agents with separate models/prompts/tools, sub-agents work in parallel on shared filesystem. Multi-agent workflow is auditable in Claude Console (inspect reasoning, task sequence, mid-workflow checkpoints). This directly validates workspace-hub's existing subagent dispatch pattern and offers official SDK support for it going forward. → [Claude Managed Agents: Dreaming, Outcomes, and Multi-Agent Orchestration Explained](https://www.developersdigest.tech/blog/claude-managed-agents-dreaming-outcomes-multi-agent) | [Anthropic Engineering: Multi-Agent Research System](https://www.anthropic.com/engineering/multi-agent-research-system)

2. **Claude Code now supports hierarchical agent spawning up to 3 levels deep (June 2026).** Parent agents can create child agents with task decomposition across multiple modules or files. Combined with fallback model configuration for resilient model chains, this enables deeper nesting of your existing subagent orchestration (currently capped at 2-level parent→child). Nested sub-agents, fallback models, and community tool marketplace now GA as of CLI 2026.6. → [New Features and Claude as Agent Provider in JetBrains IDEs](https://github.blog/changelog/2026-06-22-new-features-and-claude-as-agent-provider-preview-in-jetbrass-ides/) | [Claude Code CLI v2026.6 Release](https://github.com/anthropics/claude-code/releases)

3. **GSD framework v1.40.0 (May 2026) ships --minimal flag reducing system-prompt injection from ~12K to 700 tokens (94% reduction).** Minimal install profile ships only 6 core skills, making it viable for token-constrained sessions. GSD now under open-gsd governance (original author no longer involved). This directly impacts workspace-hub's context management strategy — the session harness can opt into minimal GSD when running deep-context subagent chains. → [GSD Framework GitHub Releases](https://github.com/gsd-build/get-shit-done/releases) | [GSD Framework: The System Revolutionizing Development](https://pasqualepillitteri.it/en/news/169/gsd-framework-claude-code-ai-development)

4. **MCP specification 2026-07-28 RC ships stateless protocol core, Extensions framework, Tasks extension, and MCP Apps.** Stateless core scales on ordinary HTTP infrastructure. Tasks extension enables long-running work (relevant to workspace-hub's overnight research automation and batch operations). MCP tunnels entered research preview (May 19) — outbound-only encrypted connection enables agents to reach customer data without inbound firewall rules. Ecosystem reached 19,831+ servers on Glama registry, 800+ on official registry (April 2026). → [MCP 2026-07-28 Release Candidate](https://blog.modelcontextprotocol.io/posts/2026-07-28-release-candidate/) | [MCP Server Ecosystem Reference 2026](https://hidekazu-konishi.com/entry/mcp_server_ecosystem_reference_2026.html) | [Model Context Protocol News 2026](https://openclaw.direct/mcp-guide/model-context-protocol-news)

5. **Codex Remote reached GA (June 2026) — remote work from mobile app with QR pairing, DigitalOcean plugin for remote workspaces, Amazon Bedrock GPT-5.6 models with reasoning-effort support.** MCP tool search by default improves tool discovery. Relevant for workspace-hub's multi-machine orchestration (dev-primary, licensed-win-1); enables approvals/monitoring from phone during long-running tasks. → [Codex as Agent Provider in JetBrains IDEs](https://github.blog/changelog/2026-07-07-codex-as-agent-provider-and-agentic-enhancements-in-jetbrains-ides/) | [Codex Changelog - July 2026](https://www.gradually.ai/en/changelogs/codex-cli/)

---

## Relevance to Project

| Finding | Affected Package/Workflow | Impact |
|---------|--------------------------|--------|
| **Anthropic Agent SDK multi-agent orchestration (May 6 beta)** | `.claude/skills/coordination/dispatching-parallel-agents`, subagent-dispatch harness, cross-review routing (Claude+Codex+Gemini per AGENTS.md) | **High.** The official SDK now supports lead-agent + specialist sub-agents in parallel with shared filesystem. Workspace-hub is already doing this pattern via `Agent` tool; SDK support validates the strategy and enables tighter integration with Claude Console auditability. Relevant to model-routing.md decision (Fable 5 = orchestration, Opus = execution) — multi-agent orchestration is now officially the orchestration layer. No breaking change, but enables tighter monitoring + formalized sub-agent context isolation. |
| **Claude Code hierarchical agents (June 2026, 3-level nesting)** | Subagent dispatch in coordinating phases/epic fan-out; multi-session parallel-work orchestration | **Medium-High.** Current subagent tree is 2-level (main → subagents). With 3-level support, can structure deeper task decomposition — e.g., main orchestrator → epic coordinator → per-issue subagents. Relevant if Phase fan-out (Phase 7 has 3 plans) grows to multi-phase coordination requiring per-phase sub-orchestrators. Fallback model support addresses the Fable 5 quota depletion incident (2026-07-04) — can set Fable as primary, Opus as fallback. |
| **GSD v1.40 --minimal (94% token reduction)** | Session harness context budget (global 2KB + workspace 4KB + project 8KB + local 2KB per CLAUDE.md); `/gsd:` workflow commands | **Medium.** Direct optimization for token-constrained scenarios. Workspace-hub uses full GSD tree; minimal profile could save ~12K tokens per deep-context subagent session (e.g., long cross-review chains or multi-repo audits). No action required (full profile still recommended for top-level sessions); mentioned for future token-budget tuning if quota pressures arise. |
| **MCP 2026-07-28 RC (stateless, Tasks extension, MCP Apps)** | Existing MCP integrations (Gmail, Calendar, Drive, doc-key-lookup); overnight research automation; long-running batch operations | **Medium.** Stateless core + Tasks extension unlocks async/long-running work without blocking the main agent. Current nightly research automation (`scripts/nightly/`) runs via detached-run pattern; Tasks extension could formalize this as MCP-native long-running workflows (e.g., `MCP.Tasks.StartAsyncResearch(...)`). MCP tunnels (research preview) enable professional-services delivery without customer firewall changes — relevant to aceengineer-website calculator CTAs + enterprise funnel. No immediate action; monitor Tasks extension stability through Q3 2026. |
| **Codex Remote GA + MCP tool search (June 2026)** | Multi-machine orchestration (dev-primary → licensed-win-1 + dev-secondary); merge-when-CLEAN automation; async task approval loops | **Low-Medium.** Codex Remote enables mobile approval/monitoring of long-running solver jobs (e.g., OrcaFlex batch runs on licensed-win-1). MCP tool search improves discovery on limited-connectivity machines (relevant to licensed-win-1 headless setup). Relevant to future "merge babysitter" patterns (scripts/operations/merge-when-clean.sh) if phone-based approval loop is desired. No breaking change; advisory for future workflow enhancement. |

---

## Recommended Actions

- [x] **Promote to PROJECT.md** — Add "AI Tooling Foundation" section documenting Q2/Q3 2026 shifts: (1) Anthropic Agent SDK multi-agent orchestration now GA, validates workspace-hub subagent dispatch strategy; (2) Claude Code 3-level agent nesting enables deeper task decomposition; (3) MCP 2026-07-28 RC stateless core + Tasks extension targets Q3 release for async workflows; (4) GSD v1.40 minimal profile available for token-constrained subagent chains. Reference `.claude/rules/model-routing.md` (Fable 5 = orchestration layer beneficiary).

- [ ] **Create GitHub issue** — `workspace-hub#TBD`: "MCP Tasks extension readiness audit — plan migration of nightly research automation (`scripts/nightly/`) from detached-run pattern to MCP Tasks when 2026-07-28 ships. Timeline: monitor July 28 RC stability, Q3 backlog if proven." Tag `lane:infrastructure`, `status:backlog`.

- [ ] **Create GitHub issue** — `workspace-hub#TBD`: "Anthropic Agent SDK integration preview — evaluate Console auditability (task sequence, reasoning inspection) for workspace-hub subagent cross-review routing. Scope: does SDK Console surface the same transparency as our manual logging, or add unique value for compliance/audit?" Tag `lane:infrastructure`, `status:backlog`.

- [ ] **Monitor** — Claude Code v2026.7+ releases (ongoing) for GA of `/doctor` command full feature set (skill/MCP server health check + optimization proposals). If available by August 2026, incorporate into `.claude/skills/coordination/pre-completion-cleanup-audit/` as a validation step.

- [ ] **Defer** — GSD v1.40 minimal profile: do NOT adopt for main-session harness (full tree is correct for orchestration). File a **reference memory** tracking the `--minimal` flag location for future deep-subagent work (not in this session, but in future token-constrained epic fan-outs).

- [ ] **Ignore with reason** — Codex Remote phone approval loop (nice-to-have, but merge-when-CLEAN shell script already handles async merge checking; phone feature targets ad-hoc approval, not automation). Revisit if licensed-win-1 batch runs become bottleneck for human attention.

---

`★ Insight ─────────────────────────────────────`
**The official AI agent SDK ecosystem is now aligned with your multi-agent orchestration patterns.** Your workspace-hub's existing subagent dispatch, lead-agent + specialist model, and Fable 5 orchestration layer strategy (per model-routing.md from July 6) are no longer home-grown — they're now validated by Anthropic's official SDK entering public beta. This is a validation win and a timing win: you've built the right mental model ahead of the SDK, and now the SDK gives you free auditability (Claude Console) + fallback-model resilience without code changes. The MCP Tasks extension (due Q3 2026) is the next piece — it will let you formalize your nightly research automation as native MCP workflows instead of detached shell scripts. No code changes needed today, but this is the roadmap for late Q3/Q4.

**Token efficiency is now a first-class concern in the multi-provider AI ecosystem.** GSD's 94% system-prompt reduction, Claude Code's fallback-model support (Opus 4.8 as Fable 5 backup when quota depletes), and the MCP stateless-core design all reflect the same insight: long AI sessions need elastic cost/quality tradeoffs, not fixed high-context defaults. The 2026-07-04 quota incident that killed Fable 5 for 3 days would be partially self-healing if fallback models were automatic. Your existing feedback_model_routing.md rule (Opus automatic fallback) is now ecosystem standard.
`─────────────────────────────────────────────────`

---

**Sources:**
- [Claude Code Docs – What's New](https://code.claude.com/docs/en/whats-new)
- [Claude Code Updates by Anthropic – Releasebot](https://releasebot.io/updates/anthropic/claude-code)
- [Claude Code June 2026: 10 New Features – SitePoint](https://www.sitepoint.com/claude-code-june-2026-10-new-features-devs-need-to-know/)
- [GSD Framework GitHub Releases](https://github.com/gsd-build/get-shit-done/releases)
- [GSD Framework: The System Revolutionizing Development – Pasquale Pillitteri](https://pasqualepillitteri.it/en/news/169/gsd-framework-claude-code-ai-development)
- [Codex as Agent Provider in JetBrains – GitHub Changelog](https://github.blog/changelog/2026-07-07-codex-as-agent-provider-and-agentic-enhancements-in-jetbrains-ides/)
- [Codex CLI Changelog – Gradually.ai](https://www.gradually.ai/en/changelogs/codex-cli/)
- [MCP 2026-07-28 Release Candidate – Model Context Protocol Blog](https://blog.modelcontextprotocol.io/posts/2026-07-28-release-candidate/)
- [MCP Server Ecosystem Reference 2026 – hidekazu-konishi.com](https://hidekazu-konishi.com/entry/mcp_server_ecosystem_reference_2026.html)
- [Model Context Protocol News 2026 – OpenClaw.Direct](https://openclaw.direct/mcp-guide/model-context-protocol-news)
- [Claude Managed Agents: Dreaming, Outcomes, and Multi-Agent Orchestration – Developers Digest](https://www.developersdigest.tech/blog/claude-managed-agents-dreaming-outcomes-multi-agent)
- [Anthropic Engineering: Multi-Agent Research System](https://www.anthropic.com/engineering/multi-agent-research-system)
- [Claude Code vs Claude Agent SDK: Which Is for What – Augment Code](https://www.augmentcode.com/tools/claude-code-vs-claude-agent-sdk)
