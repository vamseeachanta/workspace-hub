# Workspace Hub

> **Context Budget**: 4KB max | Submodules inherit and extend

## Golden Rule: Orchestrator Pattern

**Claude Code CLI is the orchestrator, NOT the executor.**

```
┌─────────────────────────────────────────────────────┐
│  Main Claude Code Instance = ORCHESTRATOR ONLY     │
│  • Plans and coordinates                           │
│  • Spawns subagents for ALL execution              │
│  • Stays lean (<20% context for planning)          │
│  • NEVER executes complex tasks directly           │
└─────────────────────────────────────────────────────┘
```

**Why?** Subagents isolate context pollution, prevent drift, and can be discarded without losing orchestrator state.

## Core Rules

1. **Orchestrate, don't execute** - Always delegate via Task tool
2. **TDD mandatory** - Tests before implementation
3. **Batch operations** - Single messages
4. **YAGNI** - Only what's needed
5. **No sycophancy** - Ask questions when unclear
6. **Use repo uv environment** - All tasks execute in project's uv environment

## Delegation Pattern

Keep main context free. Use Task tool for:
- **Explore**: codebase search, file discovery, understanding code
- **Plan**: architecture decisions, implementation strategy
- **Bash**: git operations, builds, tests
- **general-purpose**: multi-step implementations

Agents on-demand: `.claude/agent-library/<category>/<agent>.md`

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

Save plans to: `specs/modules/<module>/`
- Templates: `specs/templates/plan-template.md` or `plan-template-minimal.md`
- Required metadata: `title`, `description`, `version`, `module`, `session.id`, `session.agent`, `review`

**Cross-Review (MANDATORY)**: 3 iterations with OpenAI Codex + Google Gemini

## SPARC Modes

`/sparc-*` commands: architect, coder, reviewer, tester, planner

## Command Conventions

- `/create-spec` - Assign agents by task, use parallel subagents
- `/execute-tasks` - Use repo uv environment, mark completed tasks `[x]`

## Context Limits (MANDATORY)

| File | Max Size | Purpose |
|------|----------|---------|
| `~/.claude/CLAUDE.md` | 2KB | Global user preferences |
| Workspace `CLAUDE.md` | 4KB | Delegation patterns |
| Project `CLAUDE.md` | 8KB | Project-specific rules |
| `CLAUDE.local.md` | 2KB | User overrides |
| **Total Active** | 16KB | ~4K tokens |

**Reference docs** go in `.claude/docs/` - loaded on-demand, not in CLAUDE.md.

## Portable Configuration

### Tracked in Git
- `.claude/settings.json` - Permissions, hooks
- `.claude/agent-library/` - Agent definitions
- `.claude/docs/` - Reference documentation
- `specs/templates/` - Plan templates

### Machine-Local (NOT Synced)
- `.claude/settings.local.json` - Session permissions
- `.claude/state/` - Runtime state
- `.claude-flow/` - Runtime data

---

*Verbose documentation belongs in `.claude/docs/`, not here.*
