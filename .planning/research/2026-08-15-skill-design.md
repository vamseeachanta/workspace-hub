# Research: skill-design — 2026-08-15

## Key Findings

1. **Agent Plugins 1.0 standard published August 6, 2026 — unifies Agent Skills + MCP servers in single directory with plugin.json manifest.** Five core clients support it: VS Code, Cursor, GitHub Copilot, ChatGPT/Codex, Kiro. This is a formalization step beyond Anthropic's December 2025 agentskills.io publication (which reached ~40 products by June 2026). **Directly relevant:** workspace-hub's `.claude/skills/` directory structure now aligns with the standardized Agent Plugins 1.0 layout. No refactoring needed, but the standardization validates the existing topology. → [Agent Plugins 1.0 Standard](https://labs.cloudsecurityalliance.org/agentic/agentic-agent-registry-specification-v1/) | [Agent Skills Specification](https://agentskills.io)

2. **Anthropic Evaluations framework now published (production-grade) — recommends starting with 20–50 tasks sourced from bug reports + user failures, balanced positive/negative sets, isolated environments, monitoring for eval saturation near 100%.** Skills are increasingly treated as first-class artifacts requiring rigorous, repeatable evaluation (not deterministic binary pass/fail). The "Swiss Cheese Model" combines automated evals + production monitoring + A/B testing + user feedback + manual transcript review. **Directly relevant:** workspace-hub's existing `completeness-before-close` gate measures code coverage; Anthropic's eval framework suggests adding skill-behavior evaluation as a parallel layer (does the agent actually respect the skill's documented constraints?). → [Anthropic Evaluations Guide](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) | [Testing and Evaluating Autonomous AI Agents: Frameworks, Metrics, and Production Practices](https://zylos.ai/research/2026-07-15-agent-testing-evaluation-frameworks/)

3. **Skill descriptions must be "routing rules" (imperative, trigger-explicit) not passive documentation — use when X, always assume Y unless told otherwise, do NOT activate for Z.** Anthropic's June–August 2026 skill-authoring updates emphasize that Claude under-triggers skills by default; descriptions with explicit "when to use" conditions dramatically improve agent selection accuracy. **Directly relevant:** audit workspace-hub's 50+ skill descriptions; likely finding is passive descriptions ("this skill handles X") vs. active routing rules ("use when user asks for Y and context includes Z"). → [Skill Authoring Best Practices](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices) | [Skill Authoring Patterns from Anthropic's Best Practices](https://generativeprogrammer.com/p/skill-authoring-patterns-from-anthropics)

4. **A2A (Agent-to-Agent) protocol (Google + Linux Foundation, 2026) enables horizontal agent-to-agent discovery and delegation via Agent Cards (JSON-LD metadata with capabilities, skills, endpoints); addresses the routing-reliability bottleneck in multi-agent systems where self-claimed quality signals distort delegation incentives.** Separate from MCP (vertical tool access); A2A handles horizontal peer communication. The research finding: when agents self-report capability quality, rational delegates inflate claims, systematically routing work toward the most dishonest agents. **Directly relevant:** workspace-hub's existing T3 cross-review pattern (Claude r1 → Codex r2 → Agy r3) uses implicit quality signals (Codex is "for token-heavy work"); A2A + Agent Cards would formalize this as explicit, verifiable capability declarations. Not blocking, but relevant for Phase 999.4 (autoresearch) multi-cycle orchestration design. → [Six Agent Protocols Every AI Builder Needs to Know in 2026](https://www.mindstudio.ai/blog/six-agent-protocols-ai-builders-2026) | [The Provenance Paradox in Multi-Agent LLM Routing: Delegation Contracts and Attested Identity](https://arxiv.org/pdf/2603.18043)

5. **Progressive disclosure three-layer architecture formalized: Discovery (metadata only, ~20 lines), Activation (core instructions, trigger conditions, ~200 lines), Execution (deep context, code, detailed procedures).** This saves 80–90% of token overhead vs. loading full skill content upfront. Marked "Trial - Worth pursuing" (April 2026, Thoughtworks); now widespread adoption across Pydantic AI, Claude Code, and enterprise frameworks. **Directly relevant:** workspace-hub already implements this (SHARED_SOUL.md = discovery, SOUL.runtime.md = activation, `.claude/skills/*/SKILL.md` + companion scripts = execution). No refactoring needed; document the three-tier discipline in `.claude/skills/README.md` to help skill authors understand it explicitly. → [Progressive Disclosure in AI Agent Design](https://www.thoughtworks.com/radar/techniques/progressive-context-disclosure) | [Progressive Disclosure: the technique that helps control context](https://medium.com/@martia_es/progressive-disclosure-the-technique-that-helps-control-context-and-tokens-in-ai-agents-8d6108b09289)

---

## Relevance to Project

| Finding | Workspace Hub Component | Impact | Timeline |
|---------|---|---|---|
| **Agent Plugins 1.0 standard (Aug 6)** | `.claude/skills/` directory, plugin.json manifest (if adopted) | **LOW.** Workspace-hub's current skills topology is compatible with Agent Plugins 1.0 (skills + MCP in one tree). No refactoring needed. Optional: add a `plugin.json` manifest listing skills + MCP servers for formal registry compliance. Not blocking, nice-to-have for v1.2 ecosystem integration. | v1.2 (optional) |
| **Anthropic Evaluations framework (20-50 tasks, Swiss Cheese Model)** | Phase 7 solver-verification gate, Phase 999.4 autoresearch eval function, cross-review harness | **MEDIUM-HIGH.** Phase 7's smoke tests currently verify artifact generation + CI gates (code coverage, lint). Adding skill-behavior evaluation (does solver skill actually verify lock status?) strengthens the gate. **Recommend:** Phase 7 smoke-test checklist should include: "Solver skill constraints exercised + observed in agent trace (e.g., lock-verify behavior evident in log output)." This pairs with skill-coverage metric from prior research. | Phase 7 (implement), v1.1 (document) |
| **Skill descriptions as routing rules (imperative, trigger-explicit)** | `.claude/skills/*/SKILL.md` descriptions (50+ skills across coordination, research, infrastructure, operations) | **MEDIUM.** Quick audit: sample 10 skills, check description style. Likely finding: many are passive ("handles constraint checking") vs. active ("use when agent must verify X before Y"). **Recommend:** create exemplar rewrites + checklist for v1.1 skill-description refresh. Improves Claude's triggering accuracy without reimplementation. **Timeline: 2–3 hours audit + exemplar updates.** | v1.1 (audit + exemplars) |
| **A2A agent discovery + delegation integrity (self-claimed quality signals risk)** | Multi-provider routing (`model-routing.md`), Phase 999.4 autoresearch multi-cycle iteration, T3 cross-review harness | **MEDIUM.** Workspace-hub's existing cross-review pattern (Claude r1 → Codex r2 → Agy r3) uses implicit capability assumptions. A2A + Agent Cards would formalize this as verifiable declarations (e.g., "Codex specializes in token-heavy token-count analysis, validated by X test cases"). **Opportunity:** Phase 999.4 autoresearch could use A2A for multi-cycle specialist handoffs (researched-skill → evaluator-skill → merger-skill) with explicit capability cards. **Decision point: adopt A2A for Phase 999.4 design, or keep implicit routing?** Not blocking v1.1; forward-signal for v1.2. | Phase 999.4 design (sketch for v1.2) |
| **Progressive disclosure three-layer formalization** | SHARED_SOUL.md → SOUL.runtime.md → `.claude/skills/` + `.claude/rules/` architecture | **LOW-to-MEDIUM.** Workspace-hub already implements this correctly (and ahead of industry formalization). **Recommend:** document it explicitly in `.claude/skills/README.md` + `.claude/SOUL.md` comments so skill authors understand the three-tier discipline. No refactoring; documentation-only. Helps frame future skill-authoring guidance. | v1.1 (documentation pass) |

---

## Recommended Actions

- [x] **MEDIUM (v1.1): Audit 10-skill sample for description style — passive vs. active routing rules.** Sample across domains (coordination, research, infrastructure). **Deliverable:** checklist of skills needing description refresh + 2–3 exemplar rewrites showing active-voice, trigger-explicit descriptions. Timeline: 2–3 hours. **Reference:** [Skill Authoring Best Practices](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices).

- [x] **MEDIUM (Phase 7): Add skill-behavior evaluation to solver-verification smoke tests.** Beyond artifact generation + CI gates, verify that solver skills actually exercise their documented constraints (lock verification, state validation). **Deliverable:** Phase 7 smoke-test checklist item: "Solver skill constraints observed in agent execution trace." Pairs with prior research's skill-coverage metric. Timeline: 1 day (pair with Phase 7 design review).

- [ ] **MEDIUM (Phase 7 + v1.1 gate): Implement Anthropic Evaluations framework baseline (20–50 task set) for Phase 7 solver-verification.** Balanced positive/negative scenarios (solver succeeds, solver fails on bad input, solver correctly rejects invalid state). **Deliverable:** GitHub issue `workspace-hub#TBD: "Phase 7 evaluation suite — 25 tasks covering solver success/failure/constraint modes."` Timeline: 2–3 days; pairs with completeness-before-close gate.

- [ ] **MEDIUM-LOW (v1.1 documentation): Document workspace-hub's three-layer topology in `.claude/skills/README.md`.** Explain: SHARED_SOUL.md = discovery (cross-provider identity + gates), SOUL.runtime.md = activation (provider-specific runtime), `.claude/skills/` = execution (domain-specific work). Helps skill authors understand the tier separation. **Timeline:** 1 hour; low priority, unblocks future skill-description refresh.

- [ ] **LOW (Phase 999.4 design): Sketch A2A adoption for multi-cycle autoresearch handoffs.** If Phase 999.4 uses multiple specialized agents (researcher → validator → merger), A2A + Agent Cards could formalize delegation with explicit capability declarations + verification. **Deliverable:** 1-page sketch comparing (a) current implicit routing vs. (b) A2A explicit capability declarations. **Decision:** adopt for Phase 999.4, or defer to v1.2 as a composition/routing hygiene improvement? Make call during Phase 999.4 design. **Reference:** [Six Agent Protocols Every AI Builder Needs to Know in 2026](https://www.mindstudio.ai/blog/six-agent-protocols-ai-builders-2026).

- [ ] **LOW (monitor): Track security signal from skill marketplace — 26.1% of 31K+ skills carry vulnerabilities.** This is not workspace-hub-specific, but signals that as skill ecosystems grow, quality/security concerns emerge at scale. **Action:** quarterly review of skill dependencies for known CVEs; document in `reference_skill_ecosystem_security_baseline.md`. Recommend: isolate skill execution in sandboxed subprocess (not new for v1.1, but reinforced by data).

---

`★ Insight ─────────────────────────────────────`

**Workspace-hub is architecturally ahead on three fronts, with 2026 industry convergence now validating prior design choices:**

1. **Three-layer topology (SOUL.md → runtime → skills) is now formalized as the industry standard.** You built it that way because it made sense; Thoughtworks and others are now marking it as the canonical pattern. This is good news for long-term stability — the pattern won't break or get superseded.

2. **Skill routing rules and progressive disclosure are the current frontier for agent triggering accuracy.** Your skills exist and work; the gap is **observability** (do agents actually trigger them? do they respect documented constraints?). The Anthropic Evaluations framework + skill-coverage metric from prior research close this gap. Phase 7's smoke tests should explicitly verify constraint observability, not just artifact generation.

3. **Agent-to-Agent (A2A) protocols are the new frontier for multi-agent orchestration integrity.** Your current cross-review pattern (Claude r1 → Codex r2 → Agy r3) uses implicit capability assumptions ("Claude is good at planning, Codex at execution"). A2A would formalize this as verifiable Agent Cards, reducing routing risk where self-reported quality can distort delegation. Not blocking v1.1, but relevant for Phase 999.4's multi-cycle autoresearch if you want provable specialist delegation.

**The one immediate audit to do: skill descriptions.** Based on Anthropic's June–August guidance, your 50+ skills likely have passive descriptions ("this handles constraint checking") when they should be active routing rules ("use when agent must verify X"). A quick 10-skill sample + exemplar rewrites is a 2–3 hour lift that directly improves Claude's triggering accuracy without any code changes. This should be part of v1.1's documentation refresh.

`─────────────────────────────────────────────────`

---

## Sources

- [Agent Plugins 1.0 Standard — Cloud Security Alliance](https://labs.cloudsecurityalliance.org/agentic/agentic-agent-registry-specification-v1/)
- [Agent Skills Specification](https://agentskills.io)
- [Skill Authoring Best Practices — Claude Docs](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices)
- [Skill Authoring Patterns from Anthropic's Best Practices](https://generativeprogrammer.com/p/skill-authoring-patterns-from-anthropics)
- [Anthropic Evaluations — Production Evaluation Practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)
- [Testing and Evaluating Autonomous AI Agents: Frameworks, Metrics, and Production Practices — Zylos Research](https://zylos.ai/research/2026-07-15-agent-testing-evaluation-frameworks/)
- [Six Agent Protocols Every AI Builder Needs to Know in 2026 — MindStudio](https://www.mindstudio.ai/blog/six-agent-protocols-ai-builders-2026)
- [The Provenance Paradox in Multi-Agent LLM Routing: Delegation Contracts and Attested Identity](https://arxiv.org/pdf/2603.18043)
- [Progressive Disclosure in AI Agent Design — Thoughtworks Technology Radar](https://www.thoughtworks.com/radar/techniques/progressive-context-disclosure)
- [Progressive Disclosure: the technique that helps control context (and tokens) in AI agents — Medium](https://medium.com/@martia_es/progressive-disclosure-the-technique-that-helps-control-context-and-tokens-in-ai-agents-8d6108b09289)
- [Agent Skills in 2026: Portable, Popular, Unmeasured — Nerd Level Tech](https://nerdleveltech.com/agent-skills-portable-unmeasured)
- [The Agent Skills Ecosystem in 2026: Who's Building, What's Working, and What's Next — Agentman Blog](https://agentman.ai/blog/agent-skills-ecosystem-report-2026)

---

**Status:** This research surfaces findings from the immediate Aug 6–15, 2026 window. The Agent Plugins 1.0 standard (Aug 6) is the "news peg" for this round; the surrounding findings (routing rules, evaluations framework, A2A delegation integrity, three-layer architecture formalization) are confirmations + refinements of patterns already documented in prior research. **No blocking changes to Phase 7 or v1.1.** The actionable items are all documentation/audit-level (skill descriptions, evaluation baselines, transparency on three-tier architecture). The one design decision to defer: A2A adoption for Phase 999.4 (sketch during design phase, decide then).
