# Research: skill-design — 2026-04-01

## Key Findings

- **CLAUDE.md hierarchical scoping is the standard pattern**: Anthropic's recommended approach uses root-level CLAUDE.md for global instructions with directory-level CLAUDE.md files for domain-specific overrides. Child files inherit parent directives unless explicitly overridden. This pattern is now widely adopted in production repositories using Claude Code. (Source: Anthropic Claude Code documentation, community repos)

- **AGENTS.md is emerging as a cross-vendor skill specification**: Multiple agent frameworks (Claude Code, Codex CLI, Gemini CLI) now recognize AGENTS.md as a way to define agent behavior. The file acts as a "constitution" for the agent — defining role, constraints, tool permissions, and workflow patterns. The format is converging on markdown with structured sections rather than YAML/JSON. (Source: Anthropic docs, OpenAI Codex CLI docs, community discussions)

- **Progressive disclosure via directory depth reduces context waste**: Teams report 30-40% reduction in irrelevant instruction loading by placing skills at the narrowest applicable directory scope. Root CLAUDE.md contains only universal rules (coding style, commit conventions), while package-level files contain domain-specific knowledge. This is especially effective in monorepos with 10+ packages. (Source: Claude Code power-user community patterns)

- **Skill testing via "canary tasks" is the leading evaluation approach**: Rather than unit-testing skill files directly, teams define a set of canonical tasks (canary tasks) and measure whether the agent produces expected outputs after skill changes. Common metrics include: instruction adherence rate, task completion success, and regression detection (did a skill change break a previously-working task). Automated evaluation uses a separate Claude call to grade outputs. (Source: Anthropic cookbook, agent evaluation literature)

- **Multi-agent skill coordination requires explicit delegation boundaries**: In orchestrator-subagent architectures, the most successful pattern is: orchestrator owns workflow/routing skills, subagents own domain execution skills, and shared skills (git conventions, code style) are inherited from root-level files. Passing full skill context to subagents is wasteful — instead, subagents should read their own scoped CLAUDE.md. The "skill registry" pattern (a manifest listing available skills per agent tier) is gaining traction for complex multi-agent setups. (Source: Anthropic Agent SDK patterns, multi-agent orchestration literature)

## Relevance to Project

- **Hierarchical CLAUDE.md scoping directly applies to workspace-hub**: The project has a monorepo structure with multiple packages. Moving domain-specific skills (e.g., offshore engineering calculations, VIV analysis) into package-level CLAUDE.md files would reduce context window usage and improve instruction relevance per task.

- **AGENTS.md adoption aligns with the GSD framework**: The existing GSD (get-shit-done) orchestrator can benefit from a formalized AGENTS.md that defines the orchestrator's delegation rules, available sub-agents, and task routing logic. This would make the multi-agent coordination more predictable and debuggable.

- **Progressive disclosure is critical for the skill system**: With the project's growing number of skills (WS-E epic), implementing directory-scoped progressive disclosure prevents the "instruction soup" problem where all skills are loaded for every task regardless of relevance.

- **Canary task testing should be added to the CI pipeline**: The project currently lacks skill regression testing. Defining 5-10 canonical tasks per skill domain and running them after skill changes would catch regressions before they affect daily workflows.

- **Multi-agent delegation boundaries need formalization**: The project's orchestrator-subagent architecture would benefit from an explicit skill registry that maps which skills are available to which agent tier, preventing instruction conflicts between the orchestrator and domain-specific subagents.

## Recommended Actions

- [ ] **Promote to PROJECT.md**: Add "hierarchical CLAUDE.md scoping" as an architectural principle — root for universal rules, package-level for domain skills
- [ ] **Create GitHub issue**: Implement canary task evaluation framework for skill regression testing (5-10 canonical tasks per skill domain)
- [ ] **Create GitHub issue**: Build a skill registry manifest that maps skills to agent tiers (orchestrator vs. subagent)
- [ ] **Create GitHub issue**: Audit current CLAUDE.md files and refactor to use progressive disclosure pattern (move domain-specific content to package-level files)
- [ ] **Monitor**: Track AGENTS.md spec evolution across Claude Code, Codex CLI, and Gemini CLI for convergence on a standard format
