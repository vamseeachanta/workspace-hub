# ADR-001: Agent Coordination Model Choice
*Status: Accepted | Date: 2026-02-24 | WRK-257*

## Context

workspace-hub uses a multi-agent orchestration approach across three AI providers: Claude Code,
Codex CLI, and Gemini CLI. WRK-213 found that Codex 0.102.0 introduced a native multi-agent
role system (explorer/worker/batch roles via TOML config). The question arose: should
workspace-hub adopt Codex native roles as the coordination model, or continue with the
established skill-based approach?

WRK-213 assessed the Codex native role approach. WRK-225 assessed the plugin/skills trade-off.
At time of decision, `.claude/skills/` contained 480+ SKILL.md files across nine domains,
accessed by all three providers via symlinks.

## Decision

**Use workspace-hub agent skills (Task tool pattern) as the coordination model. Do not adopt
Codex native roles as the primary multi-agent coordination mechanism.**

Coordination operates through:
- `.claude/skills/` — skill definitions (SKILL.md format), symlinked to `.codex/skills` and `.gemini/skills`
- `.claude/agent-library/` — agent definitions invoked via the Task tool
- Task tool pattern — Claude Code as orchestrator; subagents as isolated executors

## Alternatives Considered

### 1. Codex Native Roles (explorer / worker / batch)
Codex 0.102.0 introduced TOML-configured role definitions with per-role model selection,
reasoning level, system prompt, permissions, and MCP server lists.

**Rejected because:** Roles are Codex-only. Claude Code and Gemini CLI have no equivalent
role-config mechanism. Adopting Codex roles as the primary coordination layer would leave
two of the three providers uncoordinated and require maintaining parallel coordination
configs indefinitely.

### 2. Pure Claude Code Orchestration (no shared skills)
Use Claude Code's Task tool exclusively, with all coordination logic embedded in orchestrator
prompts rather than shared SKILL.md files.

**Rejected because:** Domain knowledge would be siloed in Claude Code sessions and unavailable
to Codex CLI and Gemini CLI. The 480+ skills represent significant accumulated knowledge that
must remain accessible to all providers.

### 3. Third-Party Orchestration Framework
Adopt an external agent orchestration framework (e.g., LangGraph, AutoGen, CrewAI) as the
coordination substrate.

**Rejected because:** Introduces an external runtime dependency across all three providers.
The Task tool pattern already provides orchestration without additional infrastructure. No
cross-provider standard existed at decision time.

## Rationale

1. **Cross-provider coverage** — Skills in `.claude/skills/` are accessible to all three
   providers via symlinks (`.codex/skills → ../.claude/skills`, `.gemini/skills → ../.claude/skills`).
   Codex native roles are Codex-only; adopting them would fragment coordination.
2. **Version-controlled and improvable** — SKILL.md files are git-tracked; skills improve
   across sessions and changes propagate to all three providers automatically. Codex role
   configs would require parallel maintenance in a separate config layer.
3. **Established at scale** — The SKILL.md pattern is working across 480+ skills in nine
   domains. Displacing it for Codex native roles carries high migration cost for zero
   cross-provider gain.
4. **Orchestrator pattern alignment** — The Task tool pattern (Claude Code as orchestrator,
   subagents as executors) is documented in `.claude/docs/orchestrator-pattern.md` and
   already integrated with the work-queue system. Codex native roles would introduce a
   parallel coordination mechanism with no clear advantage over the established pattern.
5. **Complementary, not competing** — Codex roles define spawn config (model + permissions +
   MCP); skills define domain knowledge. These are different layers. Skills remain the
   coordination primitive; Codex roles can configure how Codex executes them.

## Consequences

- All multi-agent coordination uses the Task tool + agent-library + skills pattern
- New agent capabilities are added to `.claude/agent-library/`; available to all providers
- Codex is used as a cross-review executor (via skills), not as an orchestrator with its own role graph
- Codex native roles (explorer/worker/batch) may complement skill dispatch within Codex sessions
  but do not replace the shared skills layer
- Revisit this decision if Codex, Claude Code, or Gemini adopt a shared cross-provider
  coordination standard

## References
- WRK-213: Codex multi-agent roles assessment
- WRK-225: Plugins vs skills trade-off (`.claude/docs/plugins-vs-skills.md`)
- `.claude/docs/codex-roles-vs-skills.md` — detailed Codex roles vs skills analysis
- `.claude/docs/orchestrator-pattern.md` — Task tool orchestration pattern
- `.claude/agent-library/` — agent definitions registry
- `CLAUDE.md` — workspace orchestration overview
