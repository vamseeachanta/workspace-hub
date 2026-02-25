---
name: writing-plans
description: Create detailed implementation plans with granular, actionable tasks (2-5 min each). Use for multi-step development tasks requiring clear guidance. Based on obra/superpowers.
version: 1.0.0
category: development
last_updated: 2026-01-19
source: https://github.com/obra/superpowers
related_skills:
  - tdd-obra
  - brainstorming
  - subagent-driven
  - parallel-dispatch
capabilities: []
requires: []
see_also: []
---

# Writing Plans Skill

## Overview

This skill guides creating detailed implementation plans for multi-step development tasks. Plans are designed for engineers with limited codebase familiarity, with granular steps (2-5 minutes each) and complete code snippets.

## Quick Start

1. **Announce** - "I'm using the writing-plans skill to create the implementation plan."
2. **Write header** - Feature name, goal, architecture, tech stack
3. **Create tasks** - Break into 2-5 minute actionable steps
4. **Include code** - Complete snippets, not abstractions
5. **Offer execution** - Subagent-driven or parallel session

## When to Use

- Multi-step feature implementations
- Complex bug fixes requiring multiple changes
- Refactoring across multiple files
- Any task requiring more than 30 minutes
- When context needs to be preserved across sessions

## Core Principles

### DRY. YAGNI. TDD. Frequent Commits.

- **DRY** - Don't Repeat Yourself: identify common patterns
- **YAGNI** - You Aren't Gonna Need It: only what's needed now
- **TDD** - Test-Driven Development: tests before code
- **Frequent Commits** - Checkpoint progress regularly

### Assumptions

- Developer is skilled but unfamiliar with specific toolset
- Breaking work into granular steps prevents confusion
- Complete code snippets are better than abstractions
- Commands should include expected outputs

## Plan Structure

### Header Format

```markdown
# Implementation Plan: [Feature Name]

## Goal
[One sentence describing the outcome]

## Architecture
[Brief description of how this fits into the system]

## Tech Stack
- Language: [language]
- Framework: [framework]
- Testing: [test framework]
- Dependencies: [key dependencies]

## Tasks
```

### Task Format

Each task specifies:
1. Exact file paths (create/modify/test)
2. Five sequential steps:
   - Write failing test
   - Verify test failure
   - Implement minimal code
   - Verify test passes
   - Commit changes

### Task Template

```markdown
### Task 1: [Descriptive Name]

**Files:**
- Create: `path/to/new/file.ts`
- Modify: `path/to/existing/file.ts`
- Test: `path/to/test/file.test.ts`

**Step 1: Write failing test**
\`\`\`typescript
// path/to/test/file.test.ts
describe('FeatureName', () => {
  it('should do expected behavior', () => {
    // Complete test code
  });
});
\`\`\`

**Step 2: Verify test failure**
\`\`\`bash
npm test -- --grep "should do expected behavior"
# Expected: FAIL - Cannot find module 'path/to/file'
\`\`\`

**Step 3: Implement minimal code**
\`\`\`typescript
// path/to/file.ts
// Complete implementation code
\`\`\`

**Step 4: Verify test passes**
\`\`\`bash
npm test -- --grep "should do expected behavior"
# Expected: PASS
\`\`\`

**Step 5: Commit**
\`\`\`bash
git add .
git commit -m "feat: add expected behavior for FeatureName"
\`\`\`
```

## Task Granularity

### Target: 2-5 Minutes Per Task

| Too Big | Just Right | Too Small |
|---------|------------|-----------|
| "Implement authentication" | "Add password validation function" | "Add semicolon" |
| "Build API endpoints" | "Create POST /users endpoint" | "Import express" |
| "Write tests" | "Test user creation happy path" | "Add describe block" |

### Splitting Large Tasks

If a task takes longer than 5 minutes:
1. Identify sub-components
2. Create separate tasks for each
3. Add dependencies between tasks
4. Keep tests focused on one behavior

## Code Snippet Requirements

### Do Include

- Complete, copy-pasteable code
- All imports and dependencies
- Type definitions (if TypeScript)
- Error handling
- Comments for non-obvious logic

### Don't Include

- Placeholder comments (`// TODO: implement`)
- Abstract descriptions ("add the necessary code")
- Partial implementations
- Untested code

## Execution Handoff

After completing the plan, offer two approaches:

### Option 1: Subagent-Driven

Fresh subagent per task in current session.
- Best for: Independent tasks, staying in context
- Uses: subagent-driven skill

### Option 2: Parallel Session

Separate session using executing-plans skill.
- Best for: Tightly coupled tasks, long plans
- Uses: executing-plans skill in new terminal

## Plan Review Checklist

Before presenting plan:
- [ ] Header complete (goal, architecture, tech stack)
- [ ] Tasks are 2-5 minutes each
- [ ] File paths are exact
- [ ] Code snippets are complete
- [ ] Test commands include expected output
- [ ] Commits are atomic and descriptive
- [ ] Dependencies between tasks are clear

## Best Practices

### Do

1. Start with the goal, not the tasks
2. Order tasks by dependency
3. Include rollback strategies for risky changes
4. Reference existing patterns in codebase
5. Use consistent naming conventions
6. Group related tasks logically

### Don't

1. Write vague task descriptions
2. Skip the test-first steps
3. Combine unrelated changes
4. Assume prior knowledge
5. Leave out error scenarios
6. Make tasks too big or too small

## Error Handling

| Situation | Action |
|-----------|--------|
| Unclear requirements | Return to brainstorming skill |
| Task too complex | Split into smaller tasks |
| Dependency discovered | Add prerequisite task |
| Plan exceeds scope | Document out-of-scope items |

## Metrics

| Metric | Target | Description |
|--------|--------|-------------|
| Task completion rate | >95% | Tasks completable as written |
| Average task time | 2-5 min | Granular but meaningful |
| Rework rate | <10% | Tasks needing revision |
| Test coverage | 100% | Every task has tests |

## Related Skills

- [tdd-obra](../tdd-obra/SKILL.md) - Test-first methodology
- [brainstorming](../../workflows/brainstorming/SKILL.md) - Design refinement
- [subagent-driven](../subagent-driven/SKILL.md) - Plan execution
- [parallel-dispatch](../../agents/parallel-dispatch/SKILL.md) - Parallel execution

---

## Version History

- **1.0.0** (2026-01-19): Initial release adapted from obra/superpowers
