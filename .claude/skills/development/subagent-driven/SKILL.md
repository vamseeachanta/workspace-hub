---
name: subagent-driven
description: Execute implementation plans with structured subagent dispatch and two-stage
  review (spec compliance, then code quality). Based on obra/superpowers.
type: reference
version: 1.0.0
category: development
last_updated: 2026-01-19
source: https://github.com/obra/superpowers
related_skills:
- writing-plans
- tdd-obra
- code-reviewer
capabilities: []
requires: []
tags: []
---

# Subagent Driven

## Overview

This skill implements structured plan execution by dispatching independent subagents for each task, followed by mandatory two-stage reviews: specification compliance first, then code quality. Ensures systematic progress with quality gates.

## Quick Start

1. **Prepare plan** - Extract tasks to TodoWrite tracker
2. **For each task:**
   - Dispatch implementer subagent
   - Answer clarification questions
   - Run spec compliance review
   - Run code quality review
3. **Final review** - Comprehensive code review
4. **Complete** - Use finishing-a-development-branch

## When to Use

- Executing implementation plans with mostly independent tasks
- Need to remain in current session
- Quality gates required between tasks
- Context preservation across multiple steps

**Don't use when:**
- Tasks are tightly coupled
- Parallel execution preferred
- Simple, single-file changes

## Process Flow

```
Plan → [Task 1] → Implement → Spec Review → Quality Review → ✓
                                  ↓              ↓
                               Fix & Re-review if needed
       [Task 2] → Implement → Spec Review → Quality Review → ✓
       ...
       Final Review → Complete
```

## Detailed Process

### Step 1: Plan Preparation

Extract all tasks with full context:

```markdown

## Task Extraction

From plan, create TodoWrite entries:
- [ ] Task 1: [Description with full context]
- [ ] Task 2: [Description with full context]
- [ ] Task 3: [Description with full context]
```

**Important:** Provide extracted text to subagents, don't make them read plan files.
### Step 2: Per-Task Execution

For each task:

#### 2a. Dispatch Implementer

```markdown
**Implementer Subagent Prompt:**

Implement the following task:

[Complete task text from plan]

*See sub-skills for full details.*
### Step 3: Final Review

After all tasks complete:

```markdown
**Final Reviewer Subagent Prompt:**

Conduct comprehensive code review of all changes:

**Tasks completed:**
[List of all tasks]


*See sub-skills for full details.*
### Step 4: Completion

Use finishing-a-development-branch skill:
- Decide: merge to main or create PR
- Handle cleanup
- Update tracking

## Critical Rules

### Never

- Skip reviews (spec compliance OR code quality)
- Start code quality review before spec compliance passes
- Dispatch multiple implementation subagents in parallel
- Make subagents read plan files directly
- Accept reviews with unresolved issues
- Continue to next task before current passes both reviews
### Always

- Provide extracted text to subagents
- Answer clarifications before implementation
- Fix issues before re-review
- Document deviations from plan
- Run both review stages in order

## Review Order Rationale

```
1. Spec Compliance (Does it do the right thing?)
   ↓
2. Code Quality (Does it do it well?)
```

Spec first because:
- No point polishing wrong code
- Requirements drive design decisions
- Quality review assumes correct functionality

## Related Skills

- [writing-plans](../planning/writing-plans/SKILL.md) - Create implementation plans
- [tdd-obra](../tdd-obra/SKILL.md) - Test-first development
- [code-reviewer](../code-reviewer/SKILL.md) - Code quality review
- [parallel-dispatch](../../agents/parallel-dispatch/SKILL.md) - Parallel execution

---

## Version History

- **1.0.0** (2026-01-19): Initial release adapted from obra/superpowers

## Sub-Skills

- [Best Practices](best-practices/SKILL.md)
- [Error Handling](error-handling/SKILL.md)
- [Metrics](metrics/SKILL.md)
