# ADR-001: Agent Coordination Model Choice
*Status: Accepted | Date: 2026-02-20 | WRK-257*

## Context

workspace-hub uses a multi-agent orchestration approach. Two models were evaluated:
1. **Workspace-hub agent skills** — `.claude/agent-library/` definitions invoked via the Task tool; skills in `.claude/skills/`; cross-provider via symlinks to `.codex/` and `.gemini/`
2. **Codex native role system** — Codex 0.102.0 TOML role definitions in `.codex/` for multi-agent coordination

WRK-213 assessed the Codex native role approach. WRK-225 assessed the plugin/skills trade-off.

## Decision

**Use workspace-hub agent skills (Task tool pattern) as the coordination model. Do not adopt Codex native roles for multi-agent coordination.**

## Rationale

1. **Cross-provider coverage** — Agent skills in `.claude/agent-library/` and `.claude/skills/` are accessible to all three providers via symlinks. Codex native roles are Codex-only; adopting them would fragment coordination across providers.
2. **Single source of truth** — Skills and agent definitions live in one place (`.claude/`); changes propagate to Codex and Gemini automatically. Codex roles require parallel maintenance.
3. **Orchestrator pattern** — The Task tool pattern (Claude Code as orchestrator, subagents as executors) is well-established in this ecosystem. Codex native roles introduce a parallel coordination mechanism with no clear advantage.
4. **Plugin format** — The plugin SKILL.md format (WRK-225) is identical to the existing skills format; no migration needed. Codex native roles would require restructuring.

## Consequences

- All multi-agent coordination goes through the Task tool + agent-library pattern
- New agent capabilities → add to `.claude/agent-library/`; available to all providers
- Codex is used as a cross-review executor, not an orchestrator
- Revisit if Codex develops a cross-provider coordination standard

## References
- WRK-213: Codex multi-agent roles assessment
- WRK-225: Plugins vs skills trade-off (`.claude/docs/plugins-vs-skills.md`)
- `.claude/agent-library/` — agent definitions
- `CLAUDE.md` — orchestrator pattern documentation
