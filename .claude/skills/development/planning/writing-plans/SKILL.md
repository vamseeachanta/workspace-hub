---
name: writing-plans
description: Create detailed implementation plans with granular, actionable tasks (2-5 min each) and enough context for a low-context implementer.
type: reference
version: 1.1.0
category: development
last_updated: 2026-04-03
source: https://github.com/obra/superpowers
related_skills:
- tdd-obra
- subagent-driven
- brainstorming
capabilities: []
requires: []
tags: []
---

# Writing Plans

## Overview

Write plans so the implementer does not have to guess. Include exact file paths, concrete task order, test commands, expected outcomes, and minimal implementation direction.

## Core Principles

- DRY
- YAGNI
- TDD
- frequent commits
- tasks should be 2-5 minutes each when possible

## When to Use

- multi-step features
- complex bug fixes across files
- refactors with sequencing risk
- any work likely to outlast current context

## Header Template

```markdown
# <Feature Name> Implementation Plan

## Goal
<one sentence>

## Architecture
<2-3 sentences>

## Tech Stack
- language/framework/tools
```

## Task Template

```markdown
### Task N: <Descriptive Name>

**Objective:** <what this task accomplishes>

**Files:**
- Create: `path/to/new_file.py`
- Modify: `path/to/existing.py`
- Test: `tests/path/test_file.py`

**Step 1: Write failing test**
```python
# concrete test here
```

**Step 2: Run test and verify failure**
`uv run pytest tests/path/test_file.py::test_name -v`

**Step 3: Write minimal implementation**
```python
# concrete implementation here
```

**Step 4: Re-run test and verify pass**
`uv run pytest tests/path/test_file.py::test_name -v`

**Step 5: Commit**
`git add <files> && git commit -m "type: message"`
```

## Writing Process

1. Understand the requirement
2. Inspect existing code and tests
3. Design the smallest sensible approach
4. Break work into ordered tasks
5. Add exact commands and expected outputs
6. Review the plan for ambiguity
7. Save plan under `docs/plans/` when appropriate

## What Good Plans Include

- exact file paths
- copy-pasteable commands
- expected failures before implementation
- expected pass conditions after implementation
- edge cases or constraints worth checking
- explicit verification steps

## Common Mistakes

- vague tasks like "implement auth"
- missing file paths
- missing test commands
- embedding abstract advice instead of concrete steps
- tasks too large to execute confidently

## Handoff Guidance

When the plan is done, state the intended execution mode clearly:
- subagent-driven execution for isolated tasks
- sequential local execution for tightly coupled changes
- parallel sessions only when files/workstreams do not contend

## Save Convention

When saving a formal plan, prefer:
- `docs/plans/YYYY-MM-DD-feature-name.md`

## Final Check

A good plan makes implementation obvious. If the implementer must guess, the plan is incomplete.
