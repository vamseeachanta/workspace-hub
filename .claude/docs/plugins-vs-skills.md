# Plugins vs Skills — Trade-off Analysis
*WRK-225 | Generated: 2026-02-20*

---

## TL;DR

Claude Code now has an official plugin system (as of early 2026) that packages skills, agents, hooks, and MCP servers into versioned, installable units. The plugin skill format is identical to our existing SKILL.md format — skills ARE the plugin primitive. The right path is a **hybrid**: keep the bespoke skills system as-is for workspace-internal use, and selectively wrap the highest-reuse skills into plugins when we want versioned distribution or team-wide installation. A full migration of 479 skills to plugin format would carry significant overhead for zero functional gain.

---

## What Are Claude Code Plugins?

Plugins (released ~late 2025 / early 2026) are a **packaging and distribution mechanism** — not a new execution primitive. They bundle any combination of:

- **Skills** (`skills/<name>/SKILL.md`) — same SKILL.md format as standalone
- **Commands** (`commands/`) — legacy flat markdown files, same as `.claude/commands/`
- **Agents** (`agents/`) — subagent markdown definitions
- **Hooks** (`hooks/hooks.json`) — PostToolUse, PreToolUse, SessionStart, etc.
- **MCP servers** (`.mcp.json`) — external tool integrations via Model Context Protocol
- **LSP servers** (`.lsp.json`) — real-time code intelligence (go-to-definition, hover)
- **Default settings** (`settings.json`) — scoped configuration

**Plugin manifest** (`.claude-plugin/plugin.json`) defines metadata: name, version, author, description. All component directories sit at the plugin root, not inside `.claude-plugin/`.

**Invocation**: Plugin skills are namespaced — `/plugin-name:skill-name` — preventing collisions. Standalone skills keep short names like `/work` or `/reflect`.

**Installation scopes**:
- `user` — `~/.claude/settings.json` (all your projects)
- `project` — `.claude/settings.json` (team-shared via git)
- `local` — `.claude/settings.local.json` (gitignored, personal)
- `managed` — enterprise-wide (read-only)

**Loading**: Plugin MCP servers start automatically; skill descriptions load into context with a dynamic budget (2% of context window, ~16,000 char fallback). Full skill body loads only on invocation.

**Distribution**: Via git-hosted marketplace (`marketplace.json`). Install with `claude plugin install name@marketplace` or `--plugin-dir ./path` for dev/local use.

---

## Current Skills System

The workspace-hub skills system predates the official plugin mechanism and covers the same ground using standalone configuration:

| Fact | Detail |
|------|--------|
| Location | `.claude/skills/` (canonical), symlinked to `.codex/skills` and `.gemini/skills` |
| Count | 479 SKILL.md files across 9 domains |
| Format | SKILL.md with YAML frontmatter + markdown body — **identical to the official skills format** |
| Invocation | `/skill-name` (short, unnamespaced) |
| Cross-provider | Symlinks at `.codex/skills` and `.gemini/skills` expose the same files to Codex CLI and Gemini CLI |
| Load strategy | Manual (`trigger: manual`) or scheduled (`trigger: scheduled`); full body on invoke only |
| Discovery | Load-on-demand; `skills-index.yaml` and per-domain `INDEX.md` for human navigation |
| Registry | `skill-registry.yaml` (deprecated), `skills-index.yaml` (current) |
| Versioning | YAML frontmatter `version:` field, tracked manually |
| Composability | `related_skills` frontmatter; orchestrator invokes via `/skill-name` or Task tool |

Skills are structured in a rich hierarchy (`coordination/`, `engineering/`, `business/`, `data/`, etc.) with supporting files alongside SKILL.md (scripts, templates, examples). The `SKILLS_GRAPH.yaml` captures cross-skill dependencies.

---

## Comparison

| Dimension | Plugins | Skills (current) | Notes |
|-----------|---------|------------------|-------|
| **Discoverability** | Auto-discovered when installed; `/plugin` UI for browse/install | Manual load-on-demand; INDEX.md files for browsing | Skills require knowing the name; plugins have marketplace UX |
| **Invocation** | `/plugin-name:skill-name` (namespaced) | `/skill-name` (short, unnamespaced) | Skills win on brevity; plugins win on collision safety |
| **Portability across projects** | Install once at `user` scope → all projects | Must be in `.claude/skills/` of the specific project | Plugins win for multi-project reuse |
| **Portability across providers** | Claude Code only — Codex and Gemini have no plugin concept | `.codex/skills` and `.gemini/skills` symlinks share all 479 skills | Skills win decisively on cross-provider use |
| **Maintenance** | Versioned releases, `plugin update`, marketplace entry; version bump required for users to see changes | In-repo file edits; immediate effect next session | Plugins add update ceremony; skills are faster to iterate |
| **Context budget** | Same as standalone: descriptions at 2% of window, full body on invoke | Same mechanism | Identical |
| **Composability** | Plugins can bundle hooks + MCP + agents + skills together | Related skills linked via frontmatter; orchestrator chains them | Plugins add hook/MCP bundling in one installable unit |
| **Agent handoff** | Plugin skills available to subagents per scope; no special subagent handoff | Skills available in same session; subagents invoked via Task tool | Roughly equivalent |
| **MCP bundling** | MCP servers bundled and auto-started with plugin | MCP servers configured separately in `.mcp.json` | Plugins win: one install activates tools + skills together |
| **LSP integration** | Plugins can ship LSP server configs | Not possible in skills | Plugins win for language-intelligence use cases |
| **Hooks bundling** | Hooks included in plugin, activated on install | Hooks in `.claude/settings.json` maintained separately | Plugins win for shareable automation workflows |
| **Migration cost** | Low per skill (format identical); high overall (479 files, namespace changes, manifest creation) | Zero — status quo | Skills win on inertia |
| **File path constraints** | Cannot reference files outside plugin root (security sandbox); symlinks honored during cache copy | No such constraint | Skills win for workspace-spanning scripts |
| **Naming** | `plugin-name:skill-name` prefix required | Arbitrary short names like `/work`, `/reflect`, `/commit` | Skills win: our commands are highly ergonomic |
| **Version gate for updates** | Users must update plugin explicitly; version bump required | File edit is immediately live | Skills win for iterative development |

---

## Unique Plugin Capabilities

1. **MCP server bundling** — install a plugin and external tool connections (databases, APIs, services) activate automatically. No separate `.mcp.json` editing required by the user.
2. **LSP server bundling** — ship language intelligence (go-to-definition, hover types) with a plugin; not achievable via standalone skills.
3. **Hook bundling** — team-wide PostToolUse/PreToolUse automation packaged and installable without touching project settings files.
4. **Marketplace distribution** — any git repo can host a marketplace; `/plugin install` pulls and caches. Public sharing and community reuse without manual file copying.
5. **Scoped team install** — `--scope project` writes to `.claude/settings.json`, making a plugin available to all teammates who clone the repo.
6. **`settings.json` default agent** — a plugin can set a custom agent as the default for a session, giving persona-level customization.

---

## Unique Skill Capabilities

1. **Cross-provider use** — Codex CLI and Gemini CLI read from `.codex/skills` and `.gemini/skills` (symlinks to `.claude/skills`). The plugin format is Claude Code-only; no Codex or Gemini plugin equivalent exists.
2. **Unnamespaced short commands** — `/work`, `/reflect`, `/commit`, `/improve` are two-to-eight character invocations. Plugin namespacing forces `/workspace-hub:work` which would break session muscle memory and all documented workflows.
3. **No version ceremony for iteration** — editing a SKILL.md is live in the next session. Plugin users must wait for a version bump and explicit update.
4. **Workspace-spanning script references** — skills reference scripts at arbitrary relative paths (`../../../../scripts/agents/`). Plugin sandboxing disallows paths outside the plugin root.
5. **Rich frontmatter metadata** — the workspace skills frontmatter includes workspace-specific fields (`target_repos`, `tools`, `related_skills`, `scripts`, `cadence`, `auto_execute`) beyond the official SKILL.md standard, used by the skill registry and graph.
6. **479 skills with zero migration cost** — the current system works today across Claude, Codex, and Gemini with full index, graph, and registry tooling.

---

## Recommendation

**Stay with skills; selectively adopt plugin packaging for external distribution only.**

**Rationale:**

1. The SKILL.md format is already the official standard — the workspace is compliant by default. No migration needed to gain the format benefits.

2. The cross-provider requirement is a hard constraint. Codex CLI and Gemini CLI do not support the Claude plugin format. The symlink strategy (`../.claude/skills`) is the only mechanism that achieves three-provider coverage. Converting to plugins would break Codex and Gemini skill access entirely.

3. Namespaced invocation (`/workspace-hub:work`) would break every documented workflow, every WRK item plan, and every session habit. The ergonomic cost is high and the benefit is only collision-safety — which is a non-issue in a private workspace.

4. Workspace-spanning script references (e.g., `../../../../scripts/agents/session.sh`) are a structural dependency of many skills. Plugin sandboxing makes this impossible without restructuring the entire scripts hierarchy.

5. The only genuine plugin advantages (MCP bundling, LSP servers, hook bundling, marketplace install) apply to **sharing with external parties**, not internal workspace operation. None of the 479 skills are currently distributed externally.

**Where plugins DO make sense (selective adoption):**

- If a skill or toolset is extracted for community release (e.g., the work-queue system, or the marine-offshore engineering skills), wrapping it in a plugin with a `plugin.json` and marketplace entry is the right distribution mechanism.
- If a new MCP server integration is added that should activate automatically for all team members, package it as a project-scope plugin (`--scope project` in `.claude/settings.json`).
- Any new **external-facing** tooling should be built plugin-first; existing internal skills stay as-is.

**Migration path (if applicable):**

No bulk migration recommended. For selective cases:
1. Create `plugin-name/.claude-plugin/plugin.json` with metadata
2. Copy the relevant `skills/<name>/SKILL.md` files to `plugin-name/skills/<name>/SKILL.md`
3. Add supporting hooks or MCP configs if needed
4. Publish to a git-hosted marketplace
5. Leave the original skill in `.claude/skills/` for cross-provider use (or symlink back)

---

## Decision Log

- **Date**: 2026-02-20
- **WRK**: WRK-225
- **Reviewed sources**:
  - [Create plugins — Claude Code Docs](https://code.claude.com/docs/en/plugins)
  - [Extend Claude with skills — Claude Code Docs](https://code.claude.com/docs/en/skills)
  - [Plugins reference — Claude Code Docs](https://code.claude.com/docs/en/plugins-reference)
  - [Official Claude Code plugins (GitHub)](https://github.com/anthropics/claude-code/tree/main/plugins)
  - [Anthropic blog: Claude Code plugins](https://claude.com/blog/claude-code-plugins)
  - Workspace skills: `.claude/skills/coordination/workspace/work-queue/SKILL.md`, `.claude/skills/coordination/workspace/agentic-horizon/SKILL.md`
  - Workspace skill index: `.claude/skills/README.md`, `.claude/skills/coordination/workspace/INDEX.md`
  - Cross-provider symlinks confirmed: `.codex/skills -> ../.claude/skills`, `.gemini/skills -> ../.claude/skills`
- **Next review**: Revisit if (a) Codex CLI or Gemini CLI adopt the plugin format, (b) the plugin ecosystem matures to the point where community skills have strong reuse value for this domain, or (c) a cross-provider plugin standard emerges.
