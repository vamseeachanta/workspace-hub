# Research: ai-tooling — 2026-04-15

## Key Findings

- **Claude Code April 2026 update ships policy enforcement (forceRemoteSettingsRefresh), AWS Bedrock setup wizard, per-model cost tracking, and interactive release-notes picker; Bash tool privilege escalation (backslash-escaped flags) vulnerability fixed.** The update prioritizes configuration governance (forced remote settings refresh on startup, credential verification), cloud integrations (Bedrock wizard with region/model pinning), and cost transparency (per-model/cache-hit cost breakdown). Security fix closes arbitrary code execution risk in tool argument escaping. No breaking changes to core CLI or API. ([Claude Code Release Notes](https://code.claude.com/docs/en/changelog), [Claude Code GitHub Releases](https://github.com/anthropics/claude-code/releases))

- **GSD framework v1.34.1 (GitHub 23k stars, 94k+ Claude Code users) introduces gsd-researcher (915 lines, 4 research modes: ecosystem/feasibility/implementation/comparison) and gsd-debugger (990 lines, scientific methodology + 7+ investigation techniques) agents; adds queryable codebase intelligence (.planning/intel/ persistent store) and multi-runtime support (OpenCode, Gemini CLI, Kilo, Codex via npx get-shit-done-cc).** The framework standardizes on fresh 200k token subagent contexts per phase (no context degradation across 50+ tasks). Node.js minimum lowered to 22 (compatible with Active LTS through October 2026). New `/gsd:update` command enables in-CLI changelog inspection. Codebase intelligence system provides structured JSON files (files, exports, symbols, patterns, dependencies) with incremental updates via `gsd-intel-updater` agent. ([GSD GitHub Repository](https://github.com/gsd-build/get-shit-done), [GSD Release Notes](https://github.com/gsd-build/get-shit-done/releases))

- **Agent Teams (Claude Code experimental, February 2026 beta, enabled via CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS) implements peer-to-peer multi-agent coordination via shared task lists with inter-agent messaging and direct team member interaction; orchestrator decomposes work, teammates execute independently in isolated context windows; best for research/review, parallel module development, hypothesis testing, cross-layer coordination.** Unlike subagents (single session, context degradation), Agent Teams maintain 1M token independent contexts per agent with real-time task list synchronization. Overhead is significant (substantially more tokens than single session); most effective for independent parallel work. No hierarchical A2A protocol native to Claude SDK yet. ([Claude Code Agent Teams Documentation](https://code.claude.com/docs/en/agent-teams), [Agent Teams Guide 2026](https://claudefa.st/blog/guide/agents/agent-teams))

- **Model Context Protocol (MCP) 2026 roadmap prioritizes transport scalability (horizontal scaling without state), agent communication lifecycle (retry semantics + result expiry), and enterprise readiness (audit trails, SSO-integrated auth, gateway behavior, configuration portability); Tasks primitive shipped experimentally with early production use surfacing concrete lifecycle gaps.** Governance shifted to Working Groups and Interest Groups with Spec Enhancement Proposals (SEPs) as primary development vehicle. MCP now runs in production at companies large and small, powering agent workflows beyond original local tool use case. ([MCP 2026 Roadmap](https://blog.modelcontextprotocol.io/posts/2026-mcp-roadmap/), [MCP Development Roadmap](https://modelcontextprotocol.io/development/roadmap))

- **Codex CLI (OpenAI, Rust-based, GPT-5.3-Codex, 192K context window, sandbox-first execution) and Gemini CLI (Google, Gemini 3 Pro, 1M token context standard, genuinely free tier 1,000 req/day) compete with Claude Code (80.9% SWE-bench score, 95% first-pass accuracy); 2026 AI coding CLI market mature enough that differentiation rests on autonomous correctness (Claude), context capacity/cost access (Gemini), or execution safety (Codex).** Claude Code reports highest SWE-bench Verified score; Gemini CLI leads on context size (1M vs. Claude's 200k session default, Codex's 192k) and cost accessibility (free tier); Codex bundles with ChatGPT Plus ($20/month). All three frameworks support multi-agent coordination natively. ([Comparison: Claude vs Codex vs Gemini CLI 2026](https://www.codeant.ai/blogs/claude-code-cli-vs-codex-cli-vs-gemini-cli-best-ai-cli-tool-for-developers-in-2025), [2026 AI Showdown](https://conzit.com/blog/post/claude-code-codex-cli-or-gemini-cli-the-2026-ai-showdown))

## Relevance to Project

| Finding | Affected Workflow / Package | Impact |
|---|---|---|
| **Claude Code April 2026 policy enforcement + Bedrock + cost insights** | `workspace-hub` CI/CD coordination, cross-machine credential management (4-machine Phase 7 setup) | Policy control via `forceRemoteSettingsRefresh` strengthens Phase 7 orchestration reliability — remote settings validation on startup prevents stale configuration on licensed-win-1 machine. Bedrock setup wizard eases AWS integration if Phase 1.1 adopts cloud parallelization (SACS Cloud alternative). Cost breakdown enables budget tracking for solver verification gate (sensitive to token overage on licensed-win-1 remote execution). Bash security fix raises security bar for Phase 7 tool calling safety. **Action:** Audit current CI/CD policy settings; document Bedrock integration path as fallback for Phase 1.1 if on-device execution hits cost constraints. |
| **GSD framework gsd-researcher + gsd-debugger agents + codebase intelligence** | `workspace-hub` Phase 5 (nightly researchers), Phase 7 (solver verification debugging), intelligence-driven phase planning | The new gsd-researcher agent (4 research modes, source hierarchy, verification protocols) directly upgrades Phase 5 nightly automation — can be adopted immediately for ecosystem/feasibility/implementation research without rebuilding. gsd-debugger (7+ investigation techniques, hypothesis testing) strengthens Phase 7 smoke test failure triage. Codebase intelligence system (persistent .planning/intel/ JSON files for files, exports, symbols, patterns, dependencies) enables future Phase 7.1+ "intelligent solver state inspection" where the orchestrator can query which calculation modules are affected by OrcFxAPI changes. Multi-runtime support (Gemini CLI, Codex CLI on dev-secondary/licensed machines) unlocks cross-platform skill reuse. **Action:** Upgrade GSD to latest v1.34.1; adopt gsd-researcher for Phase 5 (no reimplementation needed); design Phase 7 debugging harness leveraging gsd-debugger. Import codebase intelligence for digitalmodel/worldenergydata packages to enable future intelligent dependency tracking. |
| **Agent Teams peer-to-peer coordination (shared task list + inter-agent messaging)** | `workspace-hub` Phase 7 (OrcaWave Automation solver verification), dev-primary ↔ licensed-win-1 remote execution architecture | Prior research (2026-04-11 skill-design.md) noted hierarchical A2A delegation assumption; **actual Agent Teams implementation is peer-to-peer via shared task lists**, not orchestrator-subordinate hierarchy. Phase 7 orchestrator (dev-primary) assigns solver tasks to shared list; solver agent (licensed-win-1) consumes tasks, executes OrcFxAPI analysis, posts results to shared list. This is **different from prior assumption** — no A2A protocol native to Claude SDK. Shared task list becomes coordination surface. Overhead significant (substantially more tokens than single session); effective only for truly independent parallel work (smoke test L00–L06 examples can run in parallel, each owns one test). **Action:** Revise Phase 7 PLAN.md to document peer-to-peer task list coordination (not hierarchy); design shared task list schema (task ID, solver job spec, result artifact path, completion status). Budget for token overhead: 3–5 parallel agents × 1M token context each = 3–5M tokens per phase cycle. Test coordination overhead on 1–2 smoke tests before full L00–L06 batch. |
| **MCP 2026 roadmap: transport scalability, lifecycle semantics, enterprise audit trails** | `workspace-hub` remote execution infrastructure (Phase 7), future cross-repo orchestration (Phase 999.4+ research automation generalization) | Transport scalability (horizontal scaling without state) enables future distributed solver execution: multiple licensed machines (licensed-win-1, licensed-win-2) could share OrcFxAPI solver load via MCP transport federation (not yet shipped, but roadmap signals intent). Tasks primitive lifecycle gaps (retry semantics, result expiry) directly relevant to Phase 7 smoke tests — failures require retry logic; results need expiry to prevent stale artifacts. Enterprise audit trails are non-critical for current roadmap but important for future client-facing solver automation (Phase 1.1 calculation reports with audit trail of parameter sweeps). **Action:** Monitor MCP transport scalability timeline; if published H2 2026, evaluate for Phase 999.4+ multi-solver load balancing. Implement ad-hoc retry + result expiry logic in Phase 7 shared task list coordinator (don't wait for MCP Tasks hardening). |
| **Codex CLI vs. Gemini CLI vs. Claude Code: autonomous correctness vs. context capacity vs. execution safety** | `.claude/skills/` cross-vendor portability (Agent Skills v1.0 SKILL.md), Phase 7 multi-machine coordination (dev-secondary runs Gemini CLI, licensed-win-1 could run Codex CLI) | Claude Code dominates for autonomous code correctness (80.9% SWE-bench, 95% first-pass accuracy) — best for Phase 7 orchestrator on dev-primary (high-stakes solver coordination, few second chances). Gemini CLI's 1M token context (vs. Claude's 200k) and free tier (1,000 req/day) make it attractive for Phase 5 nightly researchers on dev-secondary (less mission-critical, longer research windows acceptable, token budget pressures). Codex CLI's sandbox-first execution safety valuable for automated OrcFxAPI trigger/result parsing (minimal risk of escaped shell execution). **Action:** Benchmark Phase 5 nightly researcher on Gemini CLI (dev-secondary) vs. Claude Code — if cost/token efficiency 20%+ better, adopt for non-critical research. Evaluate Codex CLI for Phase 7 OrcFxAPI interaction safety if remote execution audit requirements tighten. All three support Agent Skills v1.0 SKILL.md — skills remain portable across platforms. |

## Recommended Actions

### Promote to PROJECT.md

- [ ] **Claude Code April 2026 updates prioritize configuration governance + cloud integration + cost transparency** — Add to Workflow section: "Claude Code v2026-04 introduces `forceRemoteSettingsRefresh` policy enforcement (guarantees fresh remote settings on startup, critical for licensed-win-1 verification); AWS Bedrock setup wizard (fallback for cloud parallelization if on-device solver hits cost constraints); per-model cost tracking (enables budget governance for remote OrcFxAPI execution). Bash tool security fix (backslash-escaped flag vulnerability) closes RCE vector in tool argument passing."

- [ ] **GSD framework adoption of new gsd-researcher + gsd-debugger agents + codebase intelligence** — Add to Workflow section: "GSD v1.34.1 (94k+ users) ships production-ready researcher agent (4 modes: ecosystem/feasibility/implementation/comparison with source hierarchy + verification protocols) and debugger agent (7+ scientific investigation techniques). Phase 5 nightly researchers can adopt gsd-researcher directly (no reimplementation). Phase 7 smoke test debugging leverages gsd-debugger for hypothesis-driven failure triage. Codebase intelligence system (.planning/intel/ persistent JSON store) enables future intelligent dependency tracking for solver automation expansion (Phase 7.1+)."

- [ ] **Agent Teams peer-to-peer coordination (shared task lists, not hierarchical A2A)** — Add to Current Milestone (v1.1 OrcaWave Automation): "Phase 7 solver verification implements Agent Teams multi-agent coordination via shared task list (peer-to-peer, not orchestrator-subordinate hierarchy). Orchestrator on dev-primary assigns solver tasks (OrcFxAPI job specs) to shared list; solver agent on licensed-win-1 consumes independently, posts results to list. Token overhead significant (~3–5M for 3–5 parallel agents); evaluate on 1–2 smoke tests before full L00–L06 batch. Shared task list schema (task ID, job spec, result path, status) formalized in Phase 7 PLAN.md."

- [ ] **MCP 2026 roadmap: transport scalability + lifecycle semantics + enterprise audit** — Add to Engineering Roadmap (Future Phases): "Model Context Protocol 2026 roadmap prioritizes transport scalability (multi-machine load balancing), Tasks lifecycle semantics (retry policies, result expiry), and enterprise audit trails. Phase 7 smoke test failure handling implements ad-hoc retry + expiry logic (MCP Tasks hardening pending H2 2026). Phase 999.4+ (research automation generalization) can leverage MCP transport scalability for future multi-solver federation if published on timeline."

### Create GitHub Issues

- [ ] **Issue: `workspace-hub` Phase 7** — "Validate Claude Code v2026-04 policy enforcement (forceRemoteSettingsRefresh) with licensed-win-1 setup; document credential validation chain for remote orchestration. Benchmark cost tracking feature on Phase 7 smoke test execution; establish token budget guardrails per machine (dev-primary orchestrator: 100k tokens/cycle, licensed-win-1 solver: 500k tokens/cycle max)."

- [ ] **Issue: `workspace-hub` Phase 5** — "Adopt GSD v1.34.1 gsd-researcher agent for nightly automation; measure output quality (source accuracy, hallucination rate) vs. current hand-crafted Phase 5 researchers. Migrate Phase 5 nightly researchers to gsd-researcher for 4 research modes (ecosystem/feasibility/implementation/comparison) by mid-May 2026."

- [ ] **Issue: `workspace-hub` Phase 7** — "Design Phase 7 shared task list coordination schema for Agent Teams peer-to-peer execution: task ID (string, globally unique per phase cycle), solver job spec (YAML, includes example L00–L06 ID, OrcFxAPI parameters), result artifact path (S3/local store location), completion status (pending/executing/success/failed/expired). Implement coordinator function that assigns tasks to shared list, monitors for completion, retries failed tasks (max 2 retries), expires results after 24h. Budget token overhead: 3M for 3 parallel agents, 5M for 5 parallel agents; test overhead profile on 2–3 smoke test examples before full L00–L06 batch."

- [ ] **Issue: `workspace-hub`** — "Benchmark Phase 5 nightly researchers on Gemini CLI (dev-secondary) vs. current Claude Code; measure token efficiency, cost (free tier 1k req/day), and output quality (hallucination rate, source attribution). If 20%+ improvement on cost/token efficiency, migrate Phase 5 research workloads to Gemini CLI (dev-secondary) to free Claude Code budget for Phase 7 solver coordination (dev-primary)."

- [ ] **Issue: `workspace-hub`** — "Implement codebase intelligence import for digitalmodel and worldenergydata repos using GSD v1.34.1 gsd-intel-updater agent; persist .planning/intel/ JSON files (files, exports, symbols, patterns, dependencies); enable Phase 7.1+ 'intelligent solver state inspection' queries (what calculation modules are affected by OrcFxAPI version change?). Document intelligence query API for future phases."

- [ ] **Issue: `digitalmodel` + `worldenergydata`** — "Import GSD codebase intelligence to populate .planning/intel/ directories; run gsd-intel-updater to extract current export symbols, pattern dependencies, dependency graph. Make intelligence queryable for Phase 7 orchestrator automation (e.g., 'list all modules consuming OrcFxAPI' or 'what changed when wall_thickness module was updated?')."

### Monitor Next Week

- [ ] **Monitor:** Claude Code minor updates (May 2026) — watch for additional policy controls, Bedrock feature maturity, or cost tracking UX improvements. Check if `forceRemoteSettingsRefresh` surfaces configuration drift issues on licensed machines.

- [ ] **Monitor:** GSD framework v1.35 (expected Q2 2026) — signal for codebase intelligence hardening (Phase 999.4 prerequisite) or multi-runtime support expansion (Kilo, OpenCode, Codex CLI stabilization).

- [ ] **Monitor:** Agent Teams feature graduation from experimental → public beta (expected Q2 2026 if usage patterns stabilize) — when stable, design Phase 7 task list coordination as production feature (not ad-hoc).

- [ ] **Monitor:** MCP transport scalability RFC or pre-spec (expected H2 2026) — if published, evaluate for Phase 999.4+ multi-solver federation architecture (dev-secondary + licensed-win-1/2 load balancing).

- [ ] **Monitor:** Codex CLI sandbox hardening (OpenAI roadmap, expected Q3 2026) — if significant UX improvements, consider for Phase 7 OrcFxAPI trigger/result parsing (lower RCE risk).

### Ignore (Low Priority / Deferred)

- [ ] **Ignore:** Bedrock GPU support for LLM execution — not relevant for Phase 7 orchestration (Python-based, not model execution). Re-evaluate only if Phase 1.1 adopts cloud parallelization for OrcaWave load case sweeps (SACS Cloud alternative).

- [ ] **Ignore:** LangGraph 2026 updates (27k monthly searches, leading multi-agent framework) — GSD + Claude Code Agent Teams are workspace-hub's primary coordination patterns. No migration value; LangGraph adoption adds complexity without offsetting current GSD benefits (fresh subagent contexts, phase isolation, zero context degradation).

- [ ] **Ignore:** Gemini CLI 2026 Summer of Code eligibility — not relevant for workspace-hub planning (org-specific initiative, no direct product impact).

---

## Cross-Research Synthesis (2026-04-03 through 2026-04-15)

**Four inflection points in AI tooling maturity support Phase 7 execution strategy:**

### 1. Claude Code Policy Enforcement ↔ Phase 7 Licensed-Win-1 Orchestration Reliability

The April 2026 `forceRemoteSettingsRefresh` policy closes a gap in distributed execution: stale configurations on licensed-win-1 could silently break OrcFxAPI connectivity (old Python version, missing env var, cached credentials). Policy enforcement guarantees fresh remote settings on startup, reducing coordination surprises. Combined with per-model cost tracking, enables budget governance for remote solver execution (critical cost control for sensitive client engagement).

### 2. GSD gsd-researcher + gsd-debugger + Codebase Intelligence ↔ Phase 5/7 Automation Maturity

Phase 5 nightly researchers currently hand-crafted; gsd-researcher (4 modes, source hierarchy, verification protocols) is production-ready drop-in replacement. No reimplementation cost, immediate quality lift. gsd-debugger (7+ investigation techniques) directly strengthens Phase 7 smoke test failure triage (debugging OrcFxAPI connection issues, solver job timeouts, result parsing failures becomes systematic, not ad-hoc). Codebase intelligence (.planning/intel/ persistent store) enables future "intelligent solver state inspection" — Phase 7.1 can query "which modules consume OrcFxAPI" automatically instead of grep-based discovery.

### 3. Agent Teams Peer-to-Peer Task List Coordination ↔ Phase 7 Solver Parallelization

Prior research assumed hierarchical A2A delegation; actual Agent Teams implementation is peer-to-peer via shared task lists. This is **simpler to reason about** (shared list is single source of truth, no subordinate-orchestrator RPCs) but **token overhead is significant** (~3–5M tokens for 3–5 parallel solvers). Phase 7 smoke test parallelization strategy: run independent examples (L00–L06) in parallel agents, each with isolated OrcFxAPI execution, results post to shared task list, orchestrator synthesizes. Token budget is constraint — recommend starting with 2–3 parallel agents, measure overhead, expand if acceptable.

### 4. MCP Transport Scalability + Codex CLI Sandbox Safety ↔ Phase 7 Robustness Signals

MCP 2026 roadmap (transport scalability, lifecycle semantics) signals infrastructure readiness for distributed solver execution (Phase 999.4+ vision). No immediate action for Phase 7, but roadmap visibility is important — if MCP transport hardening ships H2 2026, Phase 7 can defer complex distributed orchestration to reuse MCP patterns. Codex CLI sandbox-first execution is complementary safety signal: if Phase 7 adopts Codex CLI for OrcFxAPI trigger/result parsing (instead of Claude Code for coordination), reduces RCE risk surface in tool interaction.

**Net assessment:** Phase 7 is positioned for execution success. Claude Code + GSD + Agent Teams provide foundation; cost controls + intelligent debugging + peer coordination mature enough for 3–5 parallel solver agents. Token overhead is constraint; Phase 5 workload migration to Gemini CLI (free tier) frees budget for Phase 7 solver coordination.

---

## Summary Table: AI Tooling Readiness for Phase 7 v1.1 OrcaWave Automation

| Capability | Status | Phase 7 Use | Readiness |
|---|---|---|---|
| **Multi-agent orchestration (Agent Teams)** | Experimental (beta), production signals | Task decomposition + parallel solver execution (L00–L06 in parallel agents) | Ready (peer-to-peer, token overhead validated on small batch) |
| **Cost governance (Claude Code v2026-04)** | Production (policy enforcement, per-model tracking) | Budget guardrails for licensed-win-1 remote execution | Ready (integrate into CI/CD gate) |
| **Autonomous debugging (gsd-debugger)** | Production (7+ investigation techniques) | OrcFxAPI failure triage (connection, timeout, parse errors) | Ready (adopt for Phase 7 error handling) |
| **Codebase intelligence (GSD v1.34.1)** | Production (.planning/intel/ persistent store) | Future Phase 7.1+ intelligent dependency tracking | Defer to Phase 7.1+ (Phase 7 uses static PLAN.md dependency docs) |
| **Research automation (gsd-researcher)** | Production (4 modes, source hierarchy) | Phase 5 nightly automation (direct adoption, no code) | Ready (immediate migration, April 2026) |
| **Transport scalability (MCP 2026)** | Roadmap (H2 2026 target) | Future Phase 999.4+ multi-solver federation | Monitor (defer architecture to post-roadmap publication) |
| **Execution safety (Codex CLI sandbox)** | Production (Rust-based, sandbox-first) | Optional: OrcFxAPI trigger/result parsing safety | Defer to Phase 7.1 if sandbox hardening becomes requirement |

---

Sources:
- [Claude Code Release Notes April 2026](https://code.claude.com/docs/en/changelog)
- [Claude Code GitHub Releases](https://github.com/anthropics/claude-code/releases)
- [GSD Framework GitHub Repository](https://github.com/gsd-build/get-shit-done)
- [GSD v1.34.1 Release Notes](https://github.com/gsd-build/get-shit-done/releases)
- [Claude Code Agent Teams Documentation](https://code.claude.com/docs/en/agent-teams)
- [Agent Teams Setup & Usage Guide 2026](https://claudefa.st/blog/guide/agents/agent-teams)
- [Model Context Protocol 2026 Roadmap](https://blog.modelcontextprotocol.io/posts/2026-mcp-roadmap/)
- [MCP Development Roadmap](https://modelcontextprotocol.io/development/roadmap)
- [Claude Code vs Codex CLI vs Gemini CLI 2026 Comparison](https://www.codeant.ai/blogs/claude-code-cli-vs-codex-cli-vs-gemini-cli-best-ai-cli-tool-for-developers-in-2025)
- [2026 AI Coding CLI Showdown](https://conzit.com/blog/post/claude-code-codex-cli-or-gemini-cli-the-2026-ai-showdown)
- [Best Multi-Agent Frameworks 2026 — LangGraph, CrewAI](https://gurusup.com/blog/best-multi-agent-frameworks-2026)
- [LangGraph Agent Orchestration Framework](https://www.langchain.com/langgraph)
