# Orchestrator Pattern

**The main Claude Code instance is the ORCHESTRATOR, not the executor.**

## Core Principle

```
┌─────────────────────────────────────────────────────────────┐
│                    USER PROMPT                               │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              ORCHESTRATOR (Main Instance)                    │
│                                                              │
│  Responsibilities:                                           │
│  • Parse user intent                                         │
│  • Break down into subtasks                                  │
│  • Spawn appropriate subagents                               │
│  • Coordinate parallel execution                             │
│  • Synthesize results for user                               │
│                                                              │
│  Context Budget: <20% (~40k tokens)                          │
│  Contains: Plans, coordination state, summaries              │
│  Does NOT contain: Execution details, verbose output         │
└─────────────────────────────────────────────────────────────┘
           │                    │                    │
           ▼                    ▼                    ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│   SUBAGENT 1    │  │   SUBAGENT 2    │  │   SUBAGENT 3    │
│   (Explore)     │  │   (Coder)       │  │   (Tester)      │
│                 │  │                 │  │                 │
│ • Search code   │  │ • Implement     │  │ • Run tests     │
│ • Read files    │  │ • Edit files    │  │ • Validate      │
│ • Return summary│  │ • Return diff   │  │ • Return status │
└─────────────────┘  └─────────────────┘  └─────────────────┘
    (discarded)          (discarded)          (discarded)
```

## Why This Pattern?

### 1. Context Isolation

Subagent context is **completely isolated** from the orchestrator:
- 200 lines of pytest output stays in subagent
- Build errors don't pollute main context
- File contents read by subagent don't accumulate

### 2. Graceful Recovery

When things go wrong:
- Orchestrator can `/clear` without losing coordination state
- Failed subagent can be re-spawned with fresh context
- Git commits preserve actual work

### 3. Parallel Execution

Multiple subagents can run simultaneously:
```javascript
// Single message spawns parallel agents
Task("Explore auth", "Find auth implementation", "Explore")
Task("Explore db", "Find database models", "Explore")
Task("Explore api", "Find API endpoints", "Explore")
```

### 4. Prevents Context Rot

Research shows context rot degrades performance as length increases. By keeping the orchestrator lean, we:
- Maintain high-quality planning decisions
- Avoid distractor accumulation
- Keep critical information prominent

## Delegation Table

| Task Type | Subagent | Returns |
|-----------|----------|---------|
| Find files/code | `Explore` | File paths, summaries |
| Read & understand | `Explore` | Explanation, key findings |
| Implement feature | `coder` | Diff summary, files changed |
| Run tests | `tester` | Pass/fail, failing test names |
| Git operations | `Bash` | Status, commit hash |
| Multi-step work | `general-purpose` | Completion status |
| Architecture | `Plan` | Design document |

## Anti-Patterns

### Wrong: Execute in Main Context

```javascript
// BAD: Pollutes main context with 500 lines
Bash("find . -name '*.py' -exec grep -l 'class' {} \\;")
Read("/path/to/large/file.py")  // 2000 lines
Bash("pytest -v")  // 200 lines of output
```

### Right: Always Delegate

```javascript
// GOOD: Subagent handles, returns summary
Task("Find Python classes",
     "Find all Python files with class definitions, return file paths",
     "Explore")

Task("Understand auth module",
     "Read and explain the auth module structure",
     "Explore")

Task("Run and report tests",
     "Run pytest, return only failing tests with stack traces",
     "tester")
```

## When Orchestrator CAN Execute Directly

Only for lightweight coordination tasks:
- `TodoWrite` - Track progress
- `AskUserQuestion` - Clarify requirements
- Quick single-file `Read` for coordination decisions
- Simple `Bash` commands (`git status`, `ls`)

**Rule of thumb:** If output might exceed 50 lines, delegate.

## Implementation Checklist

- [ ] User prompt received
- [ ] Break into subtasks (use TodoWrite)
- [ ] Identify subagent types needed
- [ ] Spawn subagents (parallel when independent)
- [ ] Collect summaries (not raw output)
- [ ] Synthesize response for user
- [ ] Mark todos complete

## Context Budget

| Component | Budget | Purpose |
|-----------|--------|---------|
| System prompt | ~10% | Tools, instructions |
| CLAUDE.md files | ~5% | Project rules |
| Orchestrator work | ~5% | Plans, coordination |
| **Free for work** | **~80%** | Subagent spawning, user interaction |

## Related

- `/context-management` - Full context optimization guide
- `~/.claude/CLAUDE.md` - Global orchestration rules
- `.claude/agent-library/` - Available subagent types
