# Codex Roles vs Skills

## Multi-Agent Roles

Codex 0.102.0 introduced native multi-agent role configuration via `.codex/config.toml`
and per-agent `agents/role_config.toml` files. Three built-in roles: `default`, `explorer`,
`worker`. Custom roles define: model, reasoning level, system prompt, permissions, MCP servers.

### Relationship to workspace-hub skills

**Key distinction** (2026-02-19):
- Claude skills extend *what one agent knows* (semantic routing via markdown)
- Codex roles define *who gets spawned for what task* (explicit config: model + permissions + MCP)

They are **complementary layers**, not alternatives:
- Skill *content* is shared — `.codex/skills → .claude/skills` symlinks mean both providers
  read the same SKILL.md files (WRK-198–202)
- Routing *config* is provider-specific — Codex uses TOML role names; Claude Code uses
  `subagent_type` + spawn prompt + skill frontmatter `invoke:` field
- MCP servers are the common substrate — the one layer both Codex and Claude Code support
  natively and can share tooling through

### Practical decisions (workspace-hub, 2026-02-19)

1. **Keep skill content shared** via symlinks — domain logic doesn't care about routing layer
2. **Maintain routing config separately** — TOML for Codex, skill frontmatter for Claude Code
3. **MCP as bridge** — tools that must work in both providers should be MCP-served
4. **Orchestrator context is sacred** — do not issue `/clear` or session reset commands in the
   orchestrator prompt layer; route these to subagents or a separate control layer

### Default thread cap

Codex default: 6 parallel agents (configurable: `max_threads = 12+`).
workspace-hub constraint: `MAX_TEAMMATES=5` (Claude Code, git-tracked in `.claude/settings.json`).
These are independent limits — do not conflate them.
