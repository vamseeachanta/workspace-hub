---
name: parallel-dispatch
description: Dispatch multiple independent agent tasks for concurrent execution. Use when multiple unrelated failures or features need simultaneous work. Based on obra/superpowers.
version: 1.0.0
category: agents
last_updated: 2026-01-19
source: https://github.com/obra/superpowers
related_skills:
  - subagent-driven
  - multi-agent-patterns
  - writing-plans
---

# Parallel Agent Dispatch Skill

## Overview

This skill addresses scenarios where multiple independent failures or features exist across different systems. Instead of sequential investigation, create separate agent tasks that work on distinct problem domains simultaneously.

## Quick Start

1. **Identify domains** - Group failures/tasks by affected subsystem
2. **Verify independence** - Confirm no shared dependencies
3. **Create tasks** - Focused scope, clear goals, specific constraints
4. **Dispatch concurrently** - Execute all agent tasks simultaneously
5. **Integrate results** - Review, verify compatibility, run tests

## When to Use

**Use parallel dispatch when:**
- Multiple unrelated failures exist
- 3+ test files failing with different root causes
- Multiple subsystems broken independently
- Features with no shared code paths
- Independent refactoring tasks

**Avoid when:**
- Failures are interconnected
- Full system context is required
- Agents would interfere with shared resources
- Sequential ordering matters
- Debugging requires holistic view

## Decision Framework

```
Are failures related?
├── Yes → Sequential debugging
└── No → Are resources shared?
    ├── Yes → Sequential or careful coordination
    └── No → Parallel dispatch suitable
```

## Implementation Pattern

### Step 1: Domain Identification

Group failures by affected subsystem:

```
Failure Analysis:
├── approval-flow.test.ts → Approval subsystem
├── batch-completion.test.ts → Batch subsystem
├── abort-handler.test.ts → Abort subsystem
└── notification.test.ts → Notification subsystem
```

Each domain becomes one agent task.

### Step 2: Task Creation

For each domain, define:

```markdown
## Agent Task: [Domain Name]

**Scope:** [Specific files/modules]

**Goal:** [Clear objective]

**Constraints:**
- Only modify files in [scope]
- Do NOT change [protected areas]
- Must maintain [invariants]

**Deliverable:**
- [ ] Tests passing
- [ ] Summary of changes
- [ ] Any discovered issues
```

### Step 3: Concurrent Dispatch

Execute all tasks simultaneously:

```bash
# Terminal 1
claude -p "Fix approval flow tests. Only modify files in src/approval/..."

# Terminal 2
claude -p "Fix batch completion tests. Only modify files in src/batch/..."

# Terminal 3
claude -p "Fix abort handler tests. Only modify files in src/abort/..."
```

### Step 4: Integration

After all agents complete:
1. Review each agent's summary
2. Check for conflicts between changes
3. Run comprehensive test suite
4. Merge changes if compatible
5. Address any integration issues

## Effective Agent Prompts

### Good Prompt Characteristics

- **Focused** - One clear problem domain
- **Self-contained** - All context needed to understand
- **Constrained** - Clear boundaries on what to change
- **Measurable** - Specific success criteria

### Prompt Template

```
You are fixing [specific domain] issues.

**Context:**
[Relevant background information]

**Files in scope:**
- src/domain/file1.ts
- src/domain/file2.ts
- tests/domain/*.test.ts

**Goal:**
Fix failing tests in [test file]

**Constraints:**
- Do NOT modify files outside scope
- Do NOT change [specific things]
- Maintain [specific invariants]

**Success criteria:**
- All tests in [file] pass
- No new test failures introduced
- Changes documented in summary

Provide a summary of changes when complete.
```

### Anti-Patterns

| Bad | Good |
|-----|------|
| "Fix all the tests" | "Fix agent-tool-abort.test.ts" |
| "Make it work" | "Ensure approval flow handles null input" |
| "Update the code" | "Modify only src/approval/*.ts" |

## Resource Coordination

### Shared Resources

If agents must touch shared resources:

```markdown
**Coordination rules:**
- Agent A: Read-only access to shared/config.ts
- Agent B: Write access to shared/config.ts (primary)
- Agent C: No access to shared/

Conflict resolution: Agent B's changes take precedence
```

### File Locking Pattern

For critical files:
```
1. Agent A completes first
2. Merge Agent A's changes
3. Provide updated context to Agent B
4. Agent B continues with fresh state
```

## Verification

### Pre-Dispatch Checklist

- [ ] Domains are truly independent
- [ ] No shared file modifications
- [ ] Each task has clear scope
- [ ] Constraints prevent interference
- [ ] Success criteria are measurable

### Post-Dispatch Checklist

- [ ] All agent tasks completed
- [ ] No conflicting file changes
- [ ] Comprehensive tests pass
- [ ] Integration tests pass
- [ ] No new issues introduced

## Best Practices

### Do

1. Clearly define domain boundaries
2. Include all necessary context in prompts
3. Set explicit constraints
4. Request summaries from each agent
5. Run integration tests after merging
6. Document coordination strategy

### Don't

1. Dispatch agents for interconnected issues
2. Allow overlapping file modifications
3. Skip the integration verification
4. Assume agents won't conflict
5. Use vague success criteria
6. Dispatch more agents than needed

## Error Handling

| Situation | Action |
|-----------|--------|
| Agent touches wrong files | Re-run with stricter constraints |
| Agents conflict on shared file | Sequence those tasks |
| One agent fails | Don't block others, fix separately |
| Integration tests fail | Identify conflict, re-run affected |

## Metrics

| Metric | Target | Description |
|--------|--------|-------------|
| Parallel efficiency | >70% | Time saved vs. sequential |
| Conflict rate | <10% | Agent changes conflicting |
| First-run success | >80% | Tasks complete without re-run |
| Integration pass rate | >90% | Combined changes work |

## Related Skills

- [subagent-driven](../../development/subagent-driven/SKILL.md) - Sequential task execution
- [multi-agent-patterns](../multi-agent-patterns/SKILL.md) - Agent architectures
- [writing-plans](../../development/planning/writing-plans/SKILL.md) - Task planning

---

## Version History

- **1.0.0** (2026-01-19): Initial release adapted from obra/superpowers
