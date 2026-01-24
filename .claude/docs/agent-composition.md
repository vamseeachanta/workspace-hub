# Agent Composition and Command Chaining

> **Version**: 1.0 | **Updated**: 2026-01-24

## Overview

Agent composition chains specialized agents to complete complex workflows. Each agent handles its specialty with fresh context, producing artifacts for the next step.

| Benefit | Explanation |
|---------|-------------|
| Context isolation | Each agent starts fresh |
| Specialization | Optimized agents perform better |
| Failure recovery | Retry failed steps without restart |
| Audit trail | Each step produces reviewable artifacts |

## Common Workflows

### Feature Development
```
/plan "feature" --> /tdd --> /code --> /verify --> /code-review --> commit
```

### Bug Fix
```
/tdd (reproduce) --> /debug --> /code --> /verify --> commit
```

### Refactoring
```
/plan --> /code --> /verify --> /code-review
```

### Documentation
```
/analyze --> /document --> /verify
```

## Workflow Diagrams

### Feature Development Flow

```
┌─────────────┐
│   /plan     │ spec
└──────┬──────┘
       ▼
┌─────────────┐
│    /tdd     │ failing tests
└──────┬──────┘
       ▼
┌─────────────┐
│   /code     │ implementation
└──────┬──────┘
       ▼
┌─────────────┐
│  /verify    │──fail──┐
└──────┬──────┘        │
       │ pass          │
       ▼               │
┌─────────────┐        │
│/code-review │        │
└──────┬──────┘        │
       │ approved      │
       ▼               │
┌─────────────┐        │
│   commit    │◄──fix──┘
└─────────────┘
```

### Parallel Composition

```
           ┌─────────────┐
           │   /plan     │
           └──────┬──────┘
      ┌──────────┼──────────┐
      ▼          ▼          ▼
┌──────────┐┌──────────┐┌──────────┐
│ Task:API ││ Task:UI  ││ Task:DB  │
└────┬─────┘└────┬─────┘└────┬─────┘
      └──────────┼──────────┘
                 ▼
           ┌─────────────┐
           │  /verify    │
           └─────────────┘
```

## Best Practices

### When to Chain vs Standalone

| Scenario | Approach |
|----------|----------|
| Multi-step workflow | Chain commands |
| Complex feature | Chain with parallel tasks |
| Quick fix | Standalone `/code` |
| Exploratory work | Standalone `/analyze` |

### Chain Design Principles

1. **Single responsibility** - Each step does one thing
2. **Clear handoff** - Explicit artifacts between steps
3. **Fail fast** - Verify before proceeding
4. **Checkpoint** - Commit after major phases

## Context Management

Agents do not share memory. Pass context via artifacts.

| Method | Use Case |
|--------|----------|
| File artifacts | `specs/modules/feature.md` |
| Git history | Commit messages, diffs |
| Shared namespace | `swarm/session/[id]` |

### What to Pass Between Agents

| Pass | Do Not Pass |
|------|-------------|
| File paths | Raw file contents |
| Commit hashes | Full diffs |
| Test names | Test output |
| Error summaries | Full stack traces |

## Example Sessions

### New API Endpoint

```bash
# 1. Plan
User: /plan "Add user preferences API"
# Output: specs/modules/user-preferences-api.md

# 2. TDD
User: /tdd
# Writes tests/api/test_user_preferences.py

# 3. Implement
User: /code
# Implements src/api/user_preferences.py

# 4. Verify
User: /verify
# All tests pass

# 5. Review and commit
User: /code-review
User: commit
```

### Bug Fix with Regression

```bash
# 1. Reproduce
User: /tdd "Login fails with special chars"

# 2. Debug and fix
User: /debug
User: /code

# 3. Verify (fails - regression)
User: /verify

# 4. Fix regression and verify
User: /code "fix edge case"
User: /verify  # passes

# 5. Commit
User: commit
```

### Parallel Feature Work

```bash
# 1. Plan with task breakdown
User: /plan "User dashboard with charts"

# 2. Execute parallel (single message spawns 3 coders)
User: implement all tasks from plan

# 3. Integrate and verify
User: /code "integrate components"
User: /verify
```

## Error Handling

| Failure Point | Recovery Strategy |
|---------------|-------------------|
| `/plan` fails | Clarify requirements, retry |
| `/tdd` fails | Check spec completeness |
| `/code` fails | Simplify scope |
| `/verify` fails | Return to `/code` with errors |
| `/code-review` rejects | Address feedback, re-verify |

### Rollback Pattern

```bash
git stash                    # Save WIP
git checkout HEAD~1          # Return to known good
# Restart from /code
```

## Related Documents

- [Orchestrator Pattern](./orchestrator-pattern.md)
- [Execution Patterns](./execution-patterns.md)
- [Agents Reference](./agents.md)
