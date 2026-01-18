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

## SPARC Modes
`/sparc-*` commands available: architect, coder, reviewer, tester, planner
