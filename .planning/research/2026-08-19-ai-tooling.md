# Research: ai-tooling — 2026-08-19

## Key Findings

1. **Claude Code v2.1.232–v2.1.234 release cycle (August 13–17, 2026): Session auto-continuation at usage limits, credential masking with Linux/WSL narrower-pattern support, GitLab MR badge support in worktree view, stronger security against credential leakage in logs/scripts.** This is a rapid-fire hardening cycle, not just incremental UX improvements. The credential masking (placeholder in logs while proxy retains control of actual value) is particularly relevant to Phase 7's licensed-win-1 remote execution scenario — agent traces won't leak credentials. → [Claude Code Timeline: Release Date and Major Updates (2026)](https://www.scriptbyai.com/claude-code-timeline/) | [Claude Code Updates by Anthropic - August 2026](https://releasebot.io/updates/anthropic/claude-code) | [Havoptic — Claude Code August 2026 Releases](https://www.havoptic.com/tools/claude-code)

2. **GSD v1.8.0 (August 17, 2026): Critical Windows fix — removed dead SDK file references that triggered infinite find.exe loops; updated global-learnings path (~/.gsd/learnings → ~/.gsd/knowledge); gated roadmap progress checkbox on verification passed.** The Windows find.exe infinite loop fix is critical for any workspace-hub usage on licensed-win-1 or ace-win-1. This suggests a known blocker in v1.42.3 that's now resolved. → [Release v1.8.0 · open-gsd/gsd-core](https://github.com/open-gsd/gsd-core/releases/tag/v1.8.0) | [Open GSD Releases](https://github.com/open-gsd/gsd-core/releases)

3. **Codex CLI v0.146.1 (Aug 5) and v0.147.0 (Aug 7, 2026): MCP 2026-07-28 support (paginated discovery, multi-round requests, non-blocking startup), Agent Plugins 1.0 support, persistent conversation sections, --approve-for-me auto-approval CLI flag, cached web search for Amazon Bedrock.** This is a major ecosystem integration — Codex now speaks the new stateless MCP spec and Agent Plugins standard natively. Directly applicable to Phase 7's cross-provider review harness (Codex r2 agent now MCP-native). → [OpenAI Codex CLI Releases August 2026](https://www.havoptic.com/tools/openai-codex) | [Codex Updates by OpenAI - August 2026](https://releasebot.io/updates/openai/codex)

4. **MCP 2026-07-28 deprecations now concrete (12-month transition window): Roots, Sampling, and Logging APIs deprecated; Tasks moved to io.modelcontextprotocol/tasks extension; Distributed tracing keys standardized for cross-server tracing (replaces deprecated Logging as observability path).** The prior research confirmed the stateless spec; this confirms what's being _removed_ and the new observability model. Workspace-hub must audit any MCP tool usage for deprecated APIs. → [The 2026-07-28 Specification | Model Context Protocol Blog](https://blog.modelcontextprotocol.io/posts/2026-07-28/) | [Google Cloud MCP servers release notes](https://docs.cloud.google.com/mcp/release-notes)

5. **Anthropic Agent SDK + MCP 2026-07-28 enterprise security (August 2026): Private network tunnels enable MCP servers to communicate with Claude agents without exposing internal services to public internet; distributed tracing for multi-hop request tracking across MCP chains.** Combined with Claude Code's credential masking, this enables secure Phase 7 licensed-win-1 agent execution — agents can access internal tools via MCP tunnels, credentials stay private, traces stay observable. → [Anthropic and OpenAI Agent Orchestration: Where the Giants Stand in 2026](https://flocker.md/blog/anthropic-openai-agent-orchestration/) | [Best Practices for Multi-Agent Orchestration with Claude · anthropics/anthropic-sdk-python · Discussion](https://github.com/anthropics/anthropic-sdk-python/discussions/1313)

---

## Relevance to Project

| Finding | Affected Component | Impact | Timeline |
|---------|---|---|---|
| **Claude Code v2.1.234 session auto-continuation + credential masking** | Phase 7 solver-verification gate, licensed-win-1 remote execution, agent trace security | **HIGH.** Session auto-continuation (when usage limits reset) eliminates manual resumption friction in long-running solver verification runs. Credential masking (log-safe placeholders) is critical for Phase 7's security posture — agent execution traces won't accidentally leak API keys or solver credentials. **Recommend:** upgrade Claude Code to v2.1.234+ before Phase 7 implementation; document credential masking in Phase 7 security checklist. | Phase 7 (this week) |
| **GSD v1.8.0 Windows find.exe fix** | GSD framework stability on licensed-win-1 / ace-win-1, phase-transition workflows | **MEDIUM.** If workspace-hub runs `/gsd:transition` commands on Windows boxes, the v1.42.3 find.exe infinite loop is a blocker. v1.8.0 fixes this. **Recommend:** (1) verify current GSD version on ace-win-1 and licensed-win-1 (expect v1.42.3 or similar pre-1.8.0), (2) upgrade to GSD v1.8.0 if Windows machines are in scope for phase transitions, (3) test `/gsd:transition` in a branch after upgrade. | Phase 7 (pre-smoke-test) |
| **Codex CLI v0.146.1–v0.147.0 MCP + plugin support** | Multi-provider cross-review harness (Codex r2 agent), T3 review pattern (Claude r1 → Codex r2 → Agy r3), `model-routing.md` lane execution | **MEDIUM-HIGH.** Codex is now natively MCP 2026-07-28 compliant and supports Agent Plugins 1.0. This means Codex r2 agents can access the same MCP tool ecosystem (Gmail, Calendar, Drive) without custom integration. **Opportunity:** Phase 7 cross-review can use MCP tools directly in Codex agent (no Hermes stitching needed). **Recommend:** test Codex MCP tool usage in a review branch; document Codex's MCP capabilities in `model-routing.md`. | v1.1 (optional exploration), Phase 7 (confirm capability) |
| **MCP deprecations (Roots, Sampling, Logging; 12-month transition)** | Gmail/Calendar/Drive MCP tool compliance, observability strategy, Phase 7 tracing | **MEDIUM.** The deprecated APIs have a 12-month transition window (through July 2027). Workspace-hub's current MCP tool usage (claude_ai_Gmail, etc.) should be audited to confirm they don't rely on Roots, Sampling, or Logging. **The new observability model uses distributed tracing (standardized keys, cross-server traceability).** **Recommend:** (1) audit `.claude/` MCP tool configurations for deprecated API usage (expected: none, since tools are first-party Anthropic), (2) document distributed-tracing integration point for Phase 7 solver verification observability (audit trail). | v1.1 (audit + doc), Phase 7 (observability design) |
| **Anthropic Agent SDK + MCP private network tunnels** | Phase 7 licensed-win-1 access control, solver system security, agent → solver communication path | **HIGH.** Private MCP tunnels enable agents to access internal tools (e.g., OrcaFlex solver on licensed-win-1) without exposing them to the public internet. Combined with Claude Code self-hosted environments (prior research) + Agent SDK orchestration (prior research), this is the complete secure execution stack for Phase 7. **Recommend:** sketch Phase 7 security model using MCP tunnels for solver access + Claude Code self-hosted execution (if Team plan available). | Phase 7 design (this week) |

---

## Recommended Actions

- [x] **HIGH (this week): Verify Claude Code version and upgrade to v2.1.234+ before Phase 7 implementation.** Credential masking is a must-have for secure agent execution traces. **Action:** (1) Check current Claude Code version: `claude --version`. (2) Upgrade: `claude upgrade` or via Claude Desktop Settings. (3) Document in Phase 7 security checklist: "Claude Code ≥v2.1.234 required for credential-safe agent execution traces." **Timeline: 15 minutes.** → [Claude Code Updates by Anthropic - August 2026](https://releasebot.io/updates/anthropic/claude-code)

- [ ] **MEDIUM (pre-Phase-7): Audit GSD version on Windows machines; upgrade to v1.8.0 if running v1.42.3 or earlier.** The find.exe infinite-loop bug is Windows-specific and potentially blocking. **Action:** (1) SSH into ace-win-1 and licensed-win-1 (if Phase 7 uses them). (2) `gsd --version`. (3) If <v1.8.0, upgrade: `gsd update` or manual install. (4) Test: `gsd list-phases` or dry-run a `/gsd:transition` command locally. (5) Document result in Phase 7 readiness checklist. **Timeline: 1–2 hours (including SSH time if machines are remote).** → [Release v1.8.0 · open-gsd/gsd-core](https://github.com/open-gsd/gsd-core/releases/tag/v1.8.0)

- [ ] **MEDIUM (v1.1 exploration): Test Codex MCP tool access (Gmail, Calendar, Drive) via v0.147.0+ native MCP support.** Codex is now MCP-native, which means r2 reviews might not need Hermes stitching for tool access. **Action:** (1) Create test branch `research/codex-mcp-native`. (2) Invoke Codex with a task that requires MCP tool access (e.g., "read this Gmail thread and summarize for the code review"). (3) Observe whether Codex accesses MCP tools directly. (4) Document findings: "Codex MCP native: [yes/no], performance: [N/A/good/slow], tool coverage: [Gmail/Calendar/Drive available/not available]." **Timeline: 2–3 hours. Optional for v1.1; useful signal for Phase 7 cross-review design.** → [OpenAI Codex CLI Releases August 2026](https://www.havoptic.com/tools/openai-codex)

- [ ] **MEDIUM (v1.1 audit): Audit workspace-hub MCP tool configurations for deprecated APIs (Roots, Sampling, Logging).** The 12-month transition window through July 2027 is generous, but conformance should be documented. **Action:** (1) Search config/agents/ and .claude/ for references to "Roots", "Sampling", "Logging" in MCP tool configs. (2) Expected result: none (tools are first-party Anthropic, unlikely to use deprecated APIs). (3) Document audit result in `reference_mcp_2026_07_28_deprecation_audit.md` with conform/non-conform status. (4) If any deprecated APIs found, create GitHub issue to migrate before July 2027 transition end. **Timeline: 30 minutes.** → [The 2026-07-28 Specification | Model Context Protocol Blog](https://blog.modelcontextprotocol.io/posts/2026-07-28/)

- [ ] **HIGH (Phase 7 design decision): Incorporate MCP private network tunnels + Claude Code credential masking into Phase 7 security model sketch.** This week's findings close the gap for secure agent → solver communication. **Action:** (1) Sketch Phase 7 execution model: Claude Code (v2.1.234+) runs solver-verification agent on licensed-win-1 (or via self-hosted environment); agent accesses OrcaFlex solver via MCP tunnel (private network exposure only); agent traces masked-safe via credential masking. (2) Compare to prior design (SSH dispatch + manual orchestration). (3) Decision: adopt MCP tunnel model for Phase 7, or defer to v1.1 security hardening? (4) Update Phase 7 design document with security stack rationale. **Timeline: 2–3 hours (sketch + decision).**  Pairs with prior research's Phase 7 orchestration design recommendation (adopt Anthropic orchestration workspace). **Reference:** [Anthropic and OpenAI Agent Orchestration: Where the Giants Stand in 2026](https://flocker.md/blog/anthropic-openai-agent-orchestration/)

- [ ] **LOW (ongoing): Monitor GSD v1.8.0 stability over next 2 weeks; confirm no new find.exe or critical regressions before rolling to production machines.** GSD v1.8.0 is very recent (Aug 17); allow a short soak period. **Action:** (1) Set calendar reminder: "GSD v1.8.0 soak-period check — Sept 2, 2026." (2) Check GitHub Issues/Discussions for any new bugs reported post-v1.8.0. (3) If clean, roll out to ace-win-1/licensed-win-1. **Timeline: quarterly check; no action needed this week.** → [open-gsd/gsd-core/issues](https://github.com/open-gsd/gsd-core/issues)

---

`★ Insight ─────────────────────────────────────`

**This week's research reveals that the infrastructure pieces for Phase 7 just got significantly more mature and integrated.**

**Claude Code v2.1.234's credential masking is a direct answer to the agent-trace-security problem:** when Phase 7 solver agents run, their execution traces will include API calls, solver invocations, credential usage — all potential leak vectors if the trace is logged or reviewed. Credential masking (a placeholder in logs while the proxy retains actual-value control) means traces are now safe to store and review without redaction overhead. This is the kind of quiet-but-critical improvement that makes agent-driven infrastructure production-grade.

**GSD v1.8.0's Windows fix is another unblocking signal.** If workspace-hub uses GSD phase-transitions on Windows machines (ace-win-1, licensed-win-1), the v1.42.3 find.exe infinite loop would hang your phase-transition workflow. v1.8.0 fixes it. This is a 3-month-old issue finally resolved, clearing a known blocker.

**Codex's native MCP support + Anthropic's MCP private tunnels create a complete secure agent-tool communication stack.** Codex can now call MCP tools directly (no Hermes bridge). Agents can access internal systems (like OrcaFlex on licensed-win-1) via MCP tunnels without exposing them to the internet. The prior research established that Agent SDK orchestration is production-stable; this week confirms the underlying tool-communication layer is also hardening fast.

**The convergence is real: GSD v1.8.0 (workflow orchestration), Claude Code v2.1.234 (secure execution + session continuity), Codex MCP-native (tool access), Anthropic Agent SDK + MCP tunnels (internal system access) — these are the building blocks of Phase 7's execution model.**

**One actionable decision before Phase 7 implementation: sketch whether Phase 7 uses the new secure stack (MCP tunnels + credential masking + orchestration) or the prior simpler model (SSH dispatch + manual stitching). The secure stack is now available; the question is whether it's in scope or deferred to v1.1.** Make this call this week, before Phase 7 implementation starts.

`─────────────────────────────────────────────────`

---

## Sources

- [Claude Code Timeline: Release Date and Major Updates (2026)](https://www.scriptbyai.com/claude-code-timeline/)
- [Claude Code Updates by Anthropic - August 2026 — Releasebot](https://releasebot.io/updates/anthropic/claude-code)
- [Havoptic — Claude Code August 2026 Releases](https://www.havoptic.com/tools/claude-code)
- [Release v1.8.0 · open-gsd/gsd-core — GitHub](https://github.com/open-gsd/gsd-core/releases/tag/v1.8.0)
- [open-gsd/gsd-core Releases](https://github.com/open-gsd/gsd-core/releases)
- [OpenAI Codex CLI Releases August 2026 — Havoptic](https://www.havoptic.com/tools/openai-codex)
- [Codex Updates by OpenAI - August 2026 — Releasebot](https://releasebot.io/updates/openai/codex)
- [The 2026-07-28 Specification | Model Context Protocol Blog](https://blog.modelcontextprotocol.io/posts/2026-07-28/)
- [Google Cloud MCP servers release notes](https://docs.cloud.google.com/mcp/release-notes)
- [Anthropic and OpenAI Agent Orchestration: Where the Giants Stand in 2026 — Flocker](https://flocker.md/blog/anthropic-openai-agent-orchestration/)
- [Best Practices for Multi-Agent Orchestration with Claude · anthropics/anthropic-sdk-python · Discussion](https://github.com/anthropics/anthropic-sdk-python/discussions/1313)

---

**Summary:** This week's research (Aug 13–19, 2026) reveals three critical infrastructure improvements arriving in the same window: Claude Code credential-safe execution, GSD Windows stability, Codex MCP integration. Combined with prior research's Agent SDK orchestration + MCP tunnels (Anthropic Aug 2026), Phase 7 now has all the pieces for a secure, observable multi-agent solver verification workflow. **Immediate actions: upgrade Claude Code to v2.1.234+, audit GSD on Windows machines, sketch Phase 7 security model using the new stack.** No blocking changes to v1.1 or Phase 7 roadmap — only accelerating toward a more mature execution model.
