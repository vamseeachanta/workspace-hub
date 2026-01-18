# Workspace Hub

## Rules
- TDD mandatory
- Batch operations in single messages
- YAGNI: Only what's needed

## Delegation Pattern
Keep main context free. Use Task tool for:
- **Explore**: codebase search, file discovery, understanding code
- **Plan**: architecture decisions, implementation strategy
- **Bash**: git operations, builds, tests
- **general-purpose**: multi-step implementations

Agents on-demand: `@.claude/agent-library/<category>/<agent>.md`

### Agent Categories
- `core/` - coder, tester, reviewer, planner
- `devops/` - database, infrastructure, security-audit, observability
- `github/` - pr-manager, code-review-swarm, release-manager
- `sparc/` - specification, pseudocode, architecture

## Commands
`./scripts/workspace` | `./scripts/repository_sync`

## Skills
`/skills` for list. Load on-demand only.

## Plan Mode Convention
When using plan mode, save plan files to: `specs/modules/<module>/`
- `<module>` = relevant module name (e.g., orcaflex, orcawave, mooring, fatigue)
- Example: `specs/modules/orcaflex/riser-analysis-plan.md`
- Example: `specs/modules/hydrodynamics/rao-import-plan.md`

**Templates**: Use `specs/templates/plan-template.md` (full) or `plan-template-minimal.md`

**Required Metadata**: `title`, `description`, `version`, `module`, `session.id`, `session.agent`, `review`

**Cross-Review (MANDATORY)**: Min 3 iterations with OpenAI Codex + Google Gemini before implementation

## SPARC Modes
`/sparc-*` commands available: architect, coder, reviewer, tester, planner

---

## Portable Configuration

### Tracked in Git (Synced Across Machines)
| Path | Purpose |
|------|---------|
| `.claude/settings.json` | Permissions, hooks, environment |
| `.claude/agent-library/` | Agent definitions |
| `.claude/tools/` | Context management utilities |
| `.claude/claude-flow-config.yaml` | Claude-flow integration config |
| `skills/` | 77 skills library |
| `CLAUDE.md` | This file |

### Machine-Local (NOT Synced)
| Path | Purpose |
|------|---------|
| `.claude/settings.local.json` | Session-specific permissions |
| `.claude/state/` | Runtime state |
| `.claude/checkpoints/` | Recovery points |
| `.claude/outputs/` | Large artifacts |
| `.claude-flow/` | Claude-flow runtime data |

### New Machine Setup
```bash
# 1. Clone repository
git clone <url> workspace-hub
cd workspace-hub
git submodule update --init --recursive

# 2. Verify configuration
cat .claude/settings.json

# 3. Optional: Enable claude-flow MCP (if needed)
# npm install -g claude-flow@v3alpha
# claude mcp add claude-flow -- npx claude-flow@v3alpha

# 4. Start working - no additional setup required
```

## Claude-Flow Integration Status

**Current**: Minimal integration (hooks only)

| Feature | Status | Recommendation |
|---------|--------|----------------|
| Edit hooks | Enabled | Keep - lightweight feedback |
| MCP server | Disabled | Enable only if memory persistence needed |
| Swarm orchestration | Disabled | Use Task tool delegation instead |
| Metrics tracking | Disabled | Enable for usage analytics |

**When to enable full claude-flow:**
- Need persistent memory across sessions
- Want Q-learning task routing
- Running parallel multi-agent workflows
- Require cross-session vector search

**Current workflow (recommended):**
1. Use Task tool with subagent_type for delegation
2. Load agents from `.claude/agent-library/` on-demand
3. Use `/skills` for domain-specific capabilities
4. Native Claude Code handles context management
