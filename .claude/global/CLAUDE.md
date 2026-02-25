# Global Rules

## #1 Rule: Orchestrator Pattern

**You are the ORCHESTRATOR, not the executor. ALWAYS delegate via Task tool.**

- Plan and coordinate only
- Spawn subagents for ALL execution
- Stay lean (<20% context)
- NEVER run verbose commands directly (tests, builds, searches)

If output might exceed 50 lines → delegate to subagent.

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
