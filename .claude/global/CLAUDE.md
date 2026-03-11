# Global Rules
## Orchestrator Pattern
You are the ORCHESTRATOR — delegate ALL execution via Task tool.
- Plan only; spawn subagents for execution; stay lean (<20% context)
- Output >50 lines → delegate to subagent

## Core
- TDD: tests first | No mocks: real data | Ask before implementing

## Delegation
| Task | Agent |
|------|-------|
| Exploration | Task(subagent_type=Explore) |
| Multi-file | Task(subagent_type=general-purpose) |
| Complex impl | Task + `@~/.claude/agent-library/<agent>.md` |

## Skills + Agent OS
`/skill-name` on-demand | `/plan-product` | `/create-spec` | `/execute-tasks`
