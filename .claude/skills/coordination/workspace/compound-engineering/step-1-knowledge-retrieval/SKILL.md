---
name: compound-engineering-step-1-knowledge-retrieval
description: 'Sub-skill of compound-engineering: Step 1: Knowledge Retrieval (+4).'
version: 1.0.0
category: coordination
type: reference
scripts_exempt: true
---

# Step 1: Knowledge Retrieval (+4)

## Step 1: Knowledge Retrieval


Retrieve prior learnings relevant to this task.

```
Delegate: /knowledge advise "<task description>"
```

Surface all PAT-*, GOT-*, TIP-*, ADR-*, COR-* entries matching the task context. These inform the plan so past mistakes are not repeated and proven patterns are reused.


## Step 2: Codebase Archaeology


Explore the target codebase to understand existing patterns, architecture, and constraints.

```
Delegate: Task(subagent_type=Explore)
- Find related files, modules, and tests
- Identify existing patterns the implementation should follow
- Map dependencies and integration points
- Note any tech debt or inconsistencies
```


## Step 3: Internet Research


Search for best practices, prior art, and potential pitfalls.

```
Delegate: Task(subagent_type=general-purpose)
- WebSearch for best practices related to the task
- WebFetch relevant documentation or examples
- Identify common failure modes others have encountered
- Gather implementation options with trade-offs
```


## Step 4: Plan Synthesis


Combine knowledge retrieval + codebase archaeology + internet research into a plan.

```
Delegate: core-planner (via Task)
- Synthesize findings into a concrete plan
- Output: specs/modules/<module>/plan.md
- Include: approach, files to change, test strategy, risks
- Format: follows specs/templates/plan-template.md
```


## Plan Output


Save to `specs/modules/<module>/plan.md` with standard plan template metadata.
