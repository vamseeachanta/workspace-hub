# Execution Patterns Reference

> Load on-demand for complex multi-agent workflows

## Tool Responsibility

| Concern | Task Tool |
|---------|-----------|
| Execute work | **Yes** |
| Create files | **Always** |
| Run code | **Always** |

## Correct Pattern

```javascript
// Spawn agents via Task tool (all in ONE message)
Task("Researcher", "Analyze requirements...", "researcher")
Task("Coder", "Implement features...", "coder")
Task("Tester", "Write tests...", "tester")
TodoWrite { todos: [...] }
```

## Batching Rules

**1 MESSAGE = ALL RELATED OPERATIONS**

- All `Task()` calls together
- All file operations together
- All Bash commands together
- All TodoWrite todos in ONE call
