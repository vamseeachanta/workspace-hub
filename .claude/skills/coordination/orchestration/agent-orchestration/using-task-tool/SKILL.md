---
name: agent-orchestration-using-task-tool
description: 'Sub-skill of agent-orchestration: Using Task Tool (+1).'
version: 1.1.0
category: coordination
type: reference
scripts_exempt: true
---

# Using Task Tool (+1)

## Using Task Tool


For complex tasks, use Claude Code's Task tool:

```javascript
Task({
    description: "Complex multi-step analysis",
    prompt: "Analyze codebase and suggest improvements",
    subagent_type: "code-analyzer"
})
```

## Parallel Agent Execution


Launch multiple agents in parallel:

```javascript
// Single message with multiple Task calls
Task({ subagent_type: "researcher", ... })
Task({ subagent_type: "coder", ... })
Task({ subagent_type: "reviewer", ... })
```
