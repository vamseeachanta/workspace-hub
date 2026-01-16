# Agent & Skill Coordination Strategy

Keep main agent context lean for thought, planning, and orchestration.

## Context Budget

| Component | Target | Purpose |
|-----------|--------|---------|
| Main agent | <30k | Planning, decisions, orchestration |
| Subagents | Unlimited | Execution, research, implementation |
| Skills | On-demand | Quick commands, templates |

## Delegation Rules

### ALWAYS Delegate (via Task tool)

| Task Type | Subagent | When |
|-----------|----------|------|
| Codebase exploration | `Explore` | Understanding code, finding files |
| Multi-file changes | `general-purpose` | >3 files modified |
| Complex implementation | Load agent | Architecture, refactoring |
| Research | `Explore` | Investigating issues, docs |
| Git operations | `Bash` | commits, branches, PRs |

### NEVER in Main Context

- Reading large files (>200 lines)
- Searching entire codebase
- Multi-step implementations
- Debugging sessions
- Test execution

### Keep in Main Context

- User communication
- Task planning & prioritization
- Decision making
- Orchestrating subagents
- Final review & approval

## Workflow Pattern

```
User Request
    │
    ▼
┌─────────────────┐
│  Main Agent     │  ← Stays lean
│  - Understand   │
│  - Plan         │
│  - Delegate     │
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌───────┐ ┌───────┐
│Explore│ │general│  ← Heavy lifting
│ Agent │ │purpose│
└───────┘ └───────┘
         │
         ▼
┌─────────────────┐
│  Main Agent     │  ← Reviews results
│  - Verify       │
│  - Communicate  │
└─────────────────┘
```

## Quick Reference

### Invoke Skills
```
/database schema users
/infrastructure terraform vpc
/security-audit scan
/observability metrics
```

### Load Agents On-Demand
```
@.claude/agent-library/devops/database.md
@.claude/agent-library/core/coder.md
@.claude/agent-library/github/pr-manager.md
```

### Task Tool Delegation
```
Task(subagent_type="Explore", prompt="Find all API endpoints")
Task(subagent_type="general-purpose", prompt="Implement feature X")
Task(subagent_type="Bash", prompt="Run tests and fix failures")
```

## Anti-Patterns

❌ Reading entire files in main context
❌ Running grep/find in main context
❌ Multi-file edits without delegation
❌ Long debugging sessions in main context
❌ Loading all agents upfront

## Best Practices

✅ Use TodoWrite to plan before executing
✅ Delegate early and often
✅ One subagent per distinct task
✅ Parallel subagents when independent
✅ Load agents only when needed
✅ Use skills for quick, common tasks
