# Research: skill-design — 2026-04-04

## Key Findings

- **Agent Skills open standard (agentskills.io v0.9, v1.0 Q2 2026) standardizes SKILL.md across all vendors.** Anthropic published the Agent Skills spec in December 2025, establishing file format, capability discovery, and execution semantics as open standards. The spec uses directory-based SKILL.md format with YAML metadata + Markdown instructions, replacing project-specific AGENTS.md with a universal SKILL.md convention. v0.9 draft is live; v1.0 scheduled for H2 2026. This enables skills written once to work across Claude Code, Cursor, Gemini CLI, Codex CLI, and Antigravity IDE without modification.

- **Progressive disclosure reduces baseline context by ~90% using three-tier architecture (metadata → instructions → resources).** Best-practice pattern: Layer 1 (name + one-liner in YAML, ~80 tokens/skill), Layer 2 (full instructions loaded on-demand), Layer 3 (references/ directory for deep resources). Google Developers and Marta Fernández Garcia documented this pattern as standard in 2026. Workspace-hub's existing hierarchical CLAUDE.md structure aligns perfectly with this model; adding progressive disclosure (directory-based skill scoping) could unlock 40-60% context savings across multi-repo orchestration.

- **SkillsBench (Harbor framework) + Braintrust canary testing establish regression eval best practices.** Systematic agent skill evaluation consists of: prompt → captured run (trace + artifacts) → deterministic checks → rubric grading → score tracking over time. Canary deployment (5% traffic, 24-48h monitoring) gates skill versions to production. Regression evals protect against backsliding (near-100% pass rate expected). SkillsBench containerizes tasks with environment, deterministic verification, and oracle solutions — enabling reproducible skill benchmarking. This pattern is production-standard across enterprise AI deployments.

- **Multi-agent orchestration via hierarchical delegation with A2A protocol (Agent-to-Agent) is 2026 mainstream.** Addy Osmani's Code Agent Orchestra and arxiv/2601.13671 document delegation patterns: feature leads spawn specialists (3x decomposition without context explosion), A2A protocol standardizes inter-agent communication (negotiation, delegation, result sharing), and skill boundaries map to organizational hierarchy. GSD-2 (TypeScript process model) and Claude Agent Teams both implement hierarchical delegation. Market forecast: 40% of enterprise apps feature task-specific agents by 2026 (vs <5% in 2025).

- **Skill evaluation frameworks (Anthropic evals, OpenAI eval-skills, Confident AI) converge on production failures → eval suite feedback loop.** Instead of pre-defined canary tasks, the leading pattern extracts failed agent interactions from production, anonymizes, and adds to regression suite. This creates compounding eval quality (production issues prevent backsliding). Anthropic's "Demystifying evals" engineering post and Braintrust's framework document this pattern. Directly applicable to workspace-hub's multi-phase GSD workflows — can capture Phase 5 (nightly research) failures and convert to Phase 7 (solver verification) eval cases.

## Relevance to Project

| Finding | Affected Workflow / Package |
|---|---|
| **Agent Skills open standard (SKILL.md convergence)** | `.claude/skills/` directory currently uses project-specific naming. Migration to universal SKILL.md format enables workspace-hub skills to be published to agentskills.io registry and used by other Claude Code users. Aligns with existing skill inventory (900+ lines gsd-researcher/gsd-debugger). No immediate breaking changes, but v1.0 Q2 2026 deadline creates window to audit and standardize. |
| **Progressive disclosure (3-tier metadata → instructions → resources)** | Workspace-hub currently loads all skills at session start. Organizing skills by directory depth (universal rules at root, package-specific skills in `/digitalmodel/`, `/worldenergydata/`), with references/ subdirectories for deep resources, could reduce context window load by 40-60%. Directly impacts Phase 7 (solver verification) multi-agent coordination, where 3+ subagents run in parallel. |
| **SkillsBench + regression testing** | Phase 5 (nightly research automation) produces research outputs that feed Phase 7 (solver verification). Capturing nightly researcher failures as deterministic checks would enable early detection of skill drift. Systematic skill evaluation framework would improve reliability of OrcFxAPI smoke tests planned for Phase 7-03. |
| **Hierarchical A2A delegation protocol** | GSD-2 and Claude Agent Teams both use hierarchical delegation. Workspace-hub's Phase 7 (solver verification) involves remote Claude Code execution on licensed-win-1 (via SSH) + synchronization back to dev-primary. Formalizing skill boundaries (orchestrator skills on dev-primary, solver-specific skills on licensed-win-1) would improve delegation clarity and error recovery. |
| **Production failures → eval suite feedback loop** | Phase 5 nightly researchers + Phase 7 smoke tests generate artifacts (YAML manifests, calculation results, error logs). Systematizing failure extraction and conversion to regression test cases would create self-improving skill quality. Aligns with project's existing Phase 5 "nightly automation" and "90-day pruning" (automatic removal of stale results). |

## Recommended Actions

- [ ] **Promote to PROJECT.md:** Add under Workflow section: "Agent Skills open standard (agentskills.io v0.9, v1.0 Q2 2026) unifies SKILL.md format across vendors. All workspace-hub skills in `.claude/skills/` should target v0.9 spec by end of Q2 2026 for interoperability with Cursor, Gemini CLI, Codex CLI. Enables skill registry publication and cross-team reuse."

- [ ] **Create GitHub issue:** Implement progressive disclosure pattern for workspace-hub multi-repo context: audit `.claude/skills/` for 3-tier architecture (L1 metadata, L2 instructions, L3 references/); move domain-specific content (offshore engineering terminology, calculation module APIs, data pipeline schemas) into package-level CLAUDE.md files (e.g., `.claude/skills/digitalmodel/`, `.claude/skills/worldenergydata/`). Target: 40-60% context reduction for Phase 7 multi-agent orchestration.

- [ ] **Create GitHub issue:** Design skill evaluation framework for Phase 5 + Phase 7: (1) define 10-15 canary tasks (OrcFxAPI smoke test, YAML manifest validation, calculation accuracy benchmarks), (2) capture nightly researcher failures as regression test cases, (3) implement Braintrust-style evaluation (prompt → trace → checks → score), (4) gate Phase 7 solver verification releases with 90%+ pass rate. Target: reduce Phase 7 smoke test flakiness and enable automated rollback on regression.

- [ ] **Create GitHub issue:** Map multi-agent skill delegation boundaries for Phase 7: (1) orchestrator skills (dev-primary): workflow routing, remote SSH trigger, artifact sync, (2) solver skills (licensed-win-1): OrcFxAPI integration, YAML parsing, result extraction, (3) shared skills (both): YAML validation, standard traceability checks. Formalize via A2A protocol documentation in Phase 7 PLAN.md.

- [ ] **Monitor:** Agent Skills spec evolution toward v1.0 (Q2 2026 deadline); when published, run `/gsd:fast` job to audit workspace-hub SKILL.md files for compliance and publish high-value skills to agentskills.io registry (e.g., gsd-researcher for domain-specific knowledge extraction, Phase 5 nightly automation research modes).

- [ ] **Ignore (low priority):** AGENTS.md format standardization — the Agent Skills spec uses SKILL.md as canonical, not AGENTS.md. Update internal naming conventions when convenient, but no breaking change required. Current `.claude/agents/*.md` files remain valid; can co-exist with SKILL.md-based skills during migration window.

---

Sources:
- [Claude Code Skills Documentation](https://code.claude.com/docs/en/skills)
- [Agent Skills API Documentation](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)
- [Agent Skills Open Standard Specification](https://github.com/anthropics/skills/blob/main/spec/agent-skills-spec.md)
- [Anthropic Agent Skills: Equipping Agents for the Real World](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)
- [Agent Skills Open Standard Overview](https://agentskills.io/home)
- [Agent Skills: Anthropic's Next Bid to Define AI Standards — The New Stack](https://thenewstack.io/agent-skills-anthropics-next-bid-to-define-ai-standards/)
- [Progressive Disclosure in AI Agents — Medium](https://medium.com/@martia_es/progressive-disclosure-the-technique-that-helps-control-context-and-tokens-in-ai-agents-8d6108b09289)
- [Skills and Progressive Disclosure for Context Engineering](https://marcelcastrobr.github.io/posts/2026-01-29-Skills-Context-Engineering.html)
- [Google for Developers — Progressive Disclosure and Agent Skills](https://x.com/googledevs/status/2039359112668950986)
- [The Code Agent Orchestra — Addy Osmani](https://addyosmani.com/blog/code-agent-orchestra/)
- [Multi-Agent Systems Orchestration — arxiv/2601.13671](https://arxiv.org/html/2601.13671v1)
- [SkillsBench: Benchmarking Agent Skills — arxiv/2602.12670](https://arxiv.org/html/2602.12670v1)
- [Anthropic: Demystifying Evals for AI Agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)
- [Testing Agent Skills Systematically with Evals — OpenAI](https://developers.openai.com/blog/eval-skills)
- [Agent Evaluation Framework 2026 — Galileo](https://galileo.ai/blog/agent-evaluation-framework-metrics-rubrics-benchmarks)
- [AI Agent Evaluation Guide — Confident AI](https://www.confident-ai.com/blog/definitive-ai-agent-evaluation-guide)
- [Agent Evaluation Readiness Checklist — LangChain](https://blog.langchain.com/agent-evaluation-readiness-checklist/)
- [AI Agent Evaluation Framework — Braintrust](https://www.braintrust.dev/articles/ai-agent-evaluation-framework)
