# Research: ai-tooling — 2026-07-22

## Key Findings

1. **Claude Code /verify and /code-review behavior changed July 19 (v2.1.215): both commands now run ONLY when explicitly invoked, not automatically.** This is a departure from the auto-run inference the prior July 15 research expected. Impact: cross-review automation relying on auto-trigger patterns must switch to explicit `/code-review` or `/verify` invocation in scripts. Existing `scripts/review/plan-review-fanout.sh` and similar automation may need command-dispatch updates. → [Claude Code Changelog July 2026](https://code.claude.com/docs/en/changelog) | [Releasebot Claude Code Updates](https://releasebot.io/updates/anthropic/claude-code)

2. **Claude Code /doctor is now GA (v2.1.217, July 21) with "smarter" diagnostics for skill/MCP server health and optimization proposals.** The July 15 research flagged this as "GA of `/doctor` command full feature set (if available by August 2026)." It's now available. `/doctor` surfaces health checks for installed MCP servers, skill validity, and optimization recommendations — directly applicable to workspace-hub's pre-completion-cleanup-audit skill (which currently lacks MCP server diagnostics). → [Claude Code Changelog](https://code.claude.com/docs/en/changelog)

3. **MCP 2026-07-28 specification RC is now LIVE (as of July 28, 2026), with formal deprecation policy, stateless core, OAuth 2.1 hardening, and beta SDKs.** Prior research (July 15) mentioned the RC as pending. The RC is authoritative; 10-week validation window for Tier 1 SDK maintainers runs through mid-October 2026. **Breaking change:** older MCP 2026-01 servers will not interoperate with 2026-07-28 clients until Tier 1 SDK migrations land (~early October). → [MCP 2026-07-28 Release Candidate Blog](https://blog.modelcontextprotocol.io/posts/2026-07-28-release-candidate/) | [MCP Stateless Migration Guide](https://www.digitalapplied.com/blog/mcp-2026-07-28-spec-stateless-migration-guide)

4. **GSD framework v1.42.x (released week of May 11, 2026) ships per-phase model selection and dynamic routing with failure-tier escalation.** Advances beyond v1.40's minimal install profile (94% token reduction). Per-phase model routing allows `/gsd:` commands to select Fable 5 for planning, Opus for execution, fallback to Sonnet on quota depletion — exactly the capability model-routing.md (July 6) describes as needed but currently manual. GSD now embeds this as built-in workflow stages. → [GSD GitHub Releases](https://github.com/gsd-build/get-shit-done/releases) | [GSD Framework 58.9K stars](https://www.augmentcode.com/learn/gsd-58k-stars-claude-code)

5. **Claude Agent SDK billing model changed June 15, 2026: separate monthly "Agent SDK credit" tier distinct from Claude API subscription.** Operations impact: workspace-hub subagent dispatch now has its own billing track separate from main-session Claude Max subscription. Implication: quota tracking, cost optimization, and runaway-subagent safeguards now have distinct budgets and rate limits. Relevant to model-routing.md's cost-resilience guidance. → [Totalum Blog – Claude Agent SDK 2026](https://www.totalum.app/blog/claude-agent-sdk-totalum-2026)

6. **Zed 1.0 IDE (April 29, 2026) ships parallel agents as headline feature — Codex CLI, Claude Agent, Gemini CLI, and custom ACP agents run side-by-side in isolated threads.** Directly relevant to workspace-hub's dev-secondary (Linux CFD/FEA workload) which may benefit from parallel agent coordination on complex simulations. Unlike the Mac-only Claude Desktop, Zed is cross-platform (macOS, Linux, Windows). → [Zed 1.0 Release – Codex Knowledge Base](https://codex.danielvaughan.com/2026/05/05/codex-cli-in-zed-parallel-agents-acp-integration-ide-workflows/)

---

## Relevance to Project

| Finding | Affected Package/Workflow | Impact |
|---------|--------------------------|--------|
| **Claude Code /verify, /code-review now explicit-only (July 19)** | `.claude/skills/coordination/pre-completion-cleanup-audit`, cross-review automation in `scripts/review/` | **High.** The prior model expected auto-trigger on code changes. Automation relying on ambient auto-review now fails silently (no auto-review happens). Implication: all cross-review fanout scripts must explicitly dispatch `/code-review` or `/verify` commands to subagents, not rely on ambient invocation. Check `.claude/skills/coordination/dispatching-parallel-agents/` for any auto-trigger assumptions. |
| **Claude Code /doctor GA (July 21)** | `.claude/skills/coordination/pre-completion-cleanup-audit` (MCP server health checks) | **Medium.** `/doctor` now validates MCP server installation and health. The cleanup-audit skill currently lacks MCP-layer diagnostics. Integrate `/doctor` output into audit scoring (check MCP connectivity, version-compatibility with 2026-07-28 spec) as part of pre-completion gate. Adds a new audit dimension (MCP ecosystem health) to the CLEAN/EXPECTED/UNEXPECTED residue buckets. |
| **MCP 2026-07-28 RC live + 10-week Tier 1 SDK window (through Oct 15)** | Existing MCP integrations (Gmail, Calendar, Drive, doc-key-lookup), MCP server ecosystem compatibility | **Medium-High.** Current workspace-hub MCP tooling (claude_ai_Gmail, etc.) will remain on pre-2026-07-28 until SDK upgrades ship (early October 2026). **Breaking interop risk:** if workspace-hub upgrades Claude Code to a version shipping the new MCP client before Tier 1 SDKs migrate their servers, MCP tool calls will fail. Mitigation: pin Claude Code to a pre-2026-07-28 client version until mid-October 2026, OR upgrade and test MCP connectivity in Phase 7 solver-verification gate. |
| **GSD v1.42 per-phase model routing (May 11)** | `/gsd:` workflow commands, plan/execute separation in multi-phase work | **Medium.** GSD now embeds the per-phase model selection that model-routing.md (July 6) describes as a policy decision. Implication: workspace-hub's harness-level model-routing rules can now delegate to GSD's built-in routing for planning phases. Reduces manual subagent dispatch complexity. Recommend: test GSD v1.42.x on next `/goal` invocation (if it reaches consensus after catalog review per goal-invocation.md). |
| **Claude Agent SDK separate billing tier (June 15)** | Subagent dispatch in multi-phase work, cross-review dispatch (Claude + Codex + Agy per AGENTS.md) | **Low-Medium.** Subagent costs now show separately from main-session costs. Operational insight: can now track subagent spend independently. Implication for cost-optimization: if subagent dispatch becomes a bottleneck (high Agent SDK credit burn), can optimize lane assignments (e.g., Sonnet for r1 reviews instead of Opus) without impacting main-session quota. No action for v1.1, but relevant to cost tracking in v1.1 retrospective. |
| **Zed 1.0 parallel agents (April 29)** | Dev environment on dev-secondary (Linux CFD/FEA workload), potential multi-agent IDE workflow | **Low.** Cross-platform parallel agent IDE could benefit dev-secondary workflows (e.g., FEA parametric analysis with agent coordination). However, dev-secondary is headless (no GUI), so Zed benefit is limited unless a graphical workload emerges there. Defer this until dev-secondary requirements change. |

---

## Recommended Actions

- [x] **Create GitHub issue** — `workspace-hub#TBD`: "Claude Code /verify + /code-review now explicit-only (July 19): audit `scripts/review/` for auto-trigger assumptions; update cross-review fanout to explicitly dispatch `/code-review` or `/verify` commands instead of relying on ambient triggers. Timeline: pre-Phase-7 (blocking cleanup-audit skill validation)." Tag `priority:high`, `lane:infrastructure`, `blocking:Phase-7`.

- [x] **Promote to `.claude/skills/coordination/pre-completion-cleanup-audit/SKILL.md`** — Integrate Claude Code `/doctor` output as a new audit dimension (CLEAN/EXPECTED/UNEXPECTED residue bucket): MCP server health, version compatibility with 2026-07-28 spec. Link the integration to the live MCP 2026-07-28 RC spec (effective now). Timeline: immediate, add as AUDIT-STEP-3 in the skill checklist.

- [ ] **Create GitHub issue** — `workspace-hub#TBD`: "MCP 2026-07-28 RC interop risk assessment: Phase 7 solver-verification gate must test MCP connectivity with current Claude Code version. Decision: pin Claude Code to pre-2026-07-28 client through October 15 (end of Tier 1 SDK migration window), OR upgrade and verify MCP tool calls (Gmail, Drive, Calendar, doc-key-lookup) remain green in smoke tests. Timeline: Phase 7 plan dependency." Tag `priority:high`, `lane:infrastructure`, `blocking:Phase-7`.

- [ ] **Monitor** — GSD v1.42.x per-phase model routing (released May 2026). When next `/goal` workflow is invoked (post v1.1), test GSD's built-in routing against workspace-hub's model-routing.md policy to confirm alignment. If aligned, simplify harness-level subagent dispatch by delegating phase-level model selection to GSD. Defer detailed integration until v1.2 planning.

- [ ] **Reference memory** — Create a tracking entry for Claude Agent SDK separate billing tier (June 15) so future cost-optimization work (v1.2 retrospective) has explicit cost-per-lane visibility for subagent dispatch tuning.

- [ ] **Defer** — Zed 1.0 parallel agents (headless dev-secondary limitation). Revisit if GUI workload emerges on dev-secondary or if future phases require interactive parametric exploration with multiple agents.

- [ ] **Ignore with reason** — Claude Code security tightening for Windows (July 18): this is hygiene-only (tightens directory access controls); workspace-hub's licensed-win-1 already uses SSH + limited CLI surface, no exposure to the patched vulnerabilities.

---

`★ Insight ─────────────────────────────────────`

**The July 15 research report is already stale.** Three critical behavior changes shipped in the 7 days after that research (July 18–21): /verify + /code-review now explicit-only, /doctor is GA, and MCP 2026-07-28 RC went live. The /verify+/code-review change is a **potential blocker** for Phase 7 if cleanup-audit or cross-review automation relied on ambient triggers. The MCP 2026-07-28 interop window (10 weeks, ending Oct 15) is a **hard deadline** — you have 12 weeks to decide whether to pin Claude Code to a pre-2026-07-28 client or upgrade and test MCP compatibility.

**GSD v1.42 per-phase model routing validates workspace-hub's existing model-routing.md policy as ecosystem standard.** The July 6 rule (Fable 5 = orchestration, Opus 4.8 = execution, automatic fallback) was written as a local policy. Three weeks later, GSD ships the same pattern as a built-in feature. This is evidence that the policy is correct and increasingly standard — it's worth promoting to the rule-base as "proven ecosystem pattern" rather than "workspace-hub workaround" if the opportunity arises (e.g., a future AI-tooling foundation doc).

**The /doctor command is the missing piece for the pre-completion-cleanup-audit skill.** The audit currently checks for git/workspace residue, uncommitted changes, lock files, etc. It has no MCP-layer visibility. Now that `/doctor` is GA, the cleanup-audit can surface MCP server health (version compatibility, connectivity, plugin conflicts) as part of the EXPECTED/UNEXPECTED residue classification. This is a low-lift enhancement that adds high value to the gate.

`─────────────────────────────────────────────────`

---

## Sources

- [Claude Code Changelog – Claude Code Docs](https://code.claude.com/docs/en/changelog)
- [Releasebot – Claude Code Updates](https://releasebot.io/updates/anthropic/claude-code)
- [MCP 2026-07-28 Release Candidate – Model Context Protocol Blog](https://blog.modelcontextprotocol.io/posts/2026-07-28-release-candidate/)
- [MCP Stateless Migration Guide – Digital Applied](https://www.digitalapplied.com/blog/mcp-2026-07-28-spec-stateless-migration-guide)
- [GSD Framework GitHub Releases](https://github.com/gsd-build/get-shit-done/releases)
- [GSD Framework: 58.9K stars – Augment Code](https://www.augmentcode.com/learn/gsd-58k-stars-claude-code)
- [Totalum Blog – Claude Agent SDK in 2026](https://www.totalum.app/blog/claude-agent-sdk-totalum-2026)
- [Zed 1.0 Release – Codex Knowledge Base](https://codex.danielvaughan.com/2026/05/05/codex-cli-in-zed-parallel-agents-acp-integration-ide-workflows/)
