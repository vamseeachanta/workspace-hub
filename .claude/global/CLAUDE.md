# Global Rules

## Core
- TDD: Tests first
- No mocks: Use real data
- Ask before implementing

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
