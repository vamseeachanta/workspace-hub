# Global Rules

## Core
- TDD: Tests first
- No mocks: Use real data
- Ask before implementing

## Orchestration Model
**Claude Code CLI is the orchestrator** for all user prompts:
- Plans and coordinates work
- Spawns subagents for execution
- Stays lean - delegates heavy lifting
- Never executes complex tasks directly

## Delegation Pattern
Main agent stays lean for planning. Delegate execution to subagents:

| Task Type | Delegate To |
|-----------|-------------|
| Codebase exploration | `Task` with `subagent_type=Explore` |
| Multi-file changes | `Task` with `subagent_type=general-purpose` |
| Research/investigation | `Task` with `subagent_type=Explore` |
| Complex implementation | `Task` with agent from agent-library |

Load agents on-demand: `@~/.claude/agent-library/<agent>.md`

## Skills
Use `/skill-name` for on-demand loading. See `/skills` for list.

## Agent OS
`/plan-product` | `/create-spec` | `/execute-tasks` | `/analyze-product`
