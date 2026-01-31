---
name: compound-engineering
description: "Every.to's compound engineering - 4-phase orchestrator loop (Plan→Work→Review→Compound) where each feature makes the next easier"
version: 1.0.0
category: workspace-hub
type: skill
trigger: manual
auto_execute: false
capabilities:
  - research_driven_planning
  - codebase_archaeology
  - parallel_multi_perspective_review
  - knowledge_compounding
  - session_checkpointing
  - phase_orchestration
tools: [Read, Write, Edit, Bash, Grep, Glob, Task, WebSearch, WebFetch]
related_skills: [knowledge-manager, work-queue, claude-reflect, skill-learner]
---

# Compound Engineering Skill

Implements Every.to's compound engineering methodology as a unified orchestrator. Each feature you build makes the next one easier through systematic knowledge capture and retrieval.

## Core Loop

```
┌──────────────────────────────────────────────────┐
│              COMPOUND ENGINEERING                 │
│                                                  │
│   ┌────────┐    ┌────────┐    ┌────────┐        │
│   │  PLAN  │───▶│  WORK  │───▶│ REVIEW │        │
│   │  (40%) │    │  (10%) │    │  (40%) │        │
│   └────────┘    └────────┘    └────────┘        │
│       ▲                            │             │
│       │         ┌──────────┐       │             │
│       └─────────│ COMPOUND │◀──────┘             │
│                 │  (10%)   │                     │
│                 └──────────┘                     │
│                                                  │
│   Knowledge from past ──▶ Plan for future        │
└──────────────────────────────────────────────────┘
```

## Phase 1: PLAN (40% of effort)

The planning phase is the highest-leverage phase. Poor plans compound into poor outcomes.

### Step 1: Knowledge Retrieval

Retrieve prior learnings relevant to this task.

```
Delegate: /knowledge advise "<task description>"
```

Surface all PAT-*, GOT-*, TIP-*, ADR-*, COR-* entries matching the task context. These inform the plan so past mistakes are not repeated and proven patterns are reused.

### Step 2: Codebase Archaeology

Explore the target codebase to understand existing patterns, architecture, and constraints.

```
Delegate: Task(subagent_type=Explore)
- Find related files, modules, and tests
- Identify existing patterns the implementation should follow
- Map dependencies and integration points
- Note any tech debt or inconsistencies
```

### Step 3: Internet Research

Search for best practices, prior art, and potential pitfalls.

```
Delegate: Task(subagent_type=general-purpose)
- WebSearch for best practices related to the task
- WebFetch relevant documentation or examples
- Identify common failure modes others have encountered
- Gather implementation options with trade-offs
```

### Step 4: Plan Synthesis

Combine knowledge retrieval + codebase archaeology + internet research into a plan.

```
Delegate: core-planner (via Task)
- Synthesize findings into a concrete plan
- Output: specs/modules/<module>/plan.md
- Include: approach, files to change, test strategy, risks
- Format: follows specs/templates/plan-template.md
```

### Plan Output

Save to `specs/modules/<module>/plan.md` with standard plan template metadata.

## Phase 2: WORK (10% of effort)

With a thorough plan, implementation is the easy part.

### Execution

```
Delegate: core-coder (via Task)
- Convert plan into implementation
- TDD mandatory: tests first, then implementation
- Follow plan exactly; deviations require re-planning
- Commit after each logical unit of work
```

### Checkpoint

After work completes, save session state:

```yaml
# .claude/compound-state/<session-id>.yaml
session_id: <session-id>
task: "<task description>"
phase: work_complete
plan_ref: specs/modules/<module>/plan.md
commits: [<sha1>, <sha2>]
timestamp: <ISO-8601>
```

## Phase 3: REVIEW (40% of effort)

Spawn 12 isolated reviewer subagents in parallel, each examining the changes from a single perspective.

### 12 Review Perspectives

| # | Perspective | Focus Area |
|---|-------------|------------|
| 1 | Security | OWASP top 10, injection, auth, secrets exposure |
| 2 | Performance | Time complexity, memory usage, N+1 queries, caching |
| 3 | Correctness | Logic errors, off-by-one, null handling, edge cases |
| 4 | Maintainability | Readability, naming, complexity, single responsibility |
| 5 | Testability | Coverage gaps, untested paths, test quality |
| 6 | Scalability | Bottlenecks, horizontal scaling, data growth |
| 7 | Accessibility | WCAG compliance, screen readers, keyboard navigation |
| 8 | Error Handling | Missing catches, error messages, recovery paths |
| 9 | Dependencies | Version risks, license issues, unnecessary additions |
| 10 | Consistency | Style match, pattern adherence, convention compliance |
| 11 | Documentation | Missing docs, outdated comments, API documentation |
| 12 | Deployment | Migration needs, feature flags, rollback safety |

### Parallel Review Execution

```
For each perspective (all 12 in parallel):
  Delegate: Task(subagent_type=general-purpose)
  - Read the diff/changed files
  - Evaluate ONLY from assigned perspective
  - Output: structured findings as JSON
    {
      "perspective": "<name>",
      "severity": "critical|warning|info",
      "findings": [
        {
          "file": "<path>",
          "line": <number>,
          "issue": "<description>",
          "suggestion": "<fix>",
          "severity": "critical|warning|info"
        }
      ],
      "verdict": "pass|conditional|fail"
    }
```

### Review Aggregation

After all 12 reviewers complete:

```
Delegate: core-reviewer (via Task)
- Collect all 12 perspective reports
- Deduplicate overlapping findings
- Prioritize by severity (critical > warning > info)
- Generate unified review report
- Output: .claude/compound-reviews/<session-id>.md
- Decision: pass (proceed) | fix (iterate work phase) | redesign (back to plan)
```

### Review Verdicts

| Verdict | Action |
|---------|--------|
| All pass | Proceed to Compound phase |
| Any conditional, no critical | Fix issues, re-review affected perspectives only |
| Any critical | Return to Work phase; if architectural → return to Plan phase |

## Phase 4: COMPOUND (10% of effort)

Extract knowledge from this session so future tasks benefit.

### Knowledge Extraction

```
Delegate: Task(subagent_type=general-purpose)
- Analyze: what went well, what was surprising, what was hard
- Extract patterns (PAT-*): reusable approaches that worked
- Extract gotchas (GOT-*): traps encountered during implementation
- Extract tips (TIP-*): shortcuts or techniques discovered
- Extract decisions (ADR-*): architectural choices with rationale
- Extract corrections (COR-*): mistakes made and how they were fixed
```

### Knowledge Storage

```
Delegate: /knowledge capture
- Store each extracted entry with:
  - Confidence score based on review verdict
  - Tags linking to module, language, framework
  - Cross-references to the plan and review
```

### Skill Evolution

```
If any pattern scores > 0.7:
  Delegate: skill-learner
  - Evaluate if pattern warrants skill creation or enhancement
  - Score: (frequency * 0.3) + (cross_repo * 0.3) + (complexity * 0.2) + (time_savings * 0.2)
```

### Session Finalization

Update checkpoint:

```yaml
# .claude/compound-state/<session-id>.yaml
session_id: <session-id>
task: "<task description>"
phase: complete
plan_ref: specs/modules/<module>/plan.md
review_ref: .claude/compound-reviews/<session-id>.md
commits: [<sha1>, <sha2>, ...]
knowledge_entries: [PAT-xxx, GOT-xxx, TIP-xxx]
timestamp: <ISO-8601>
completed_at: <ISO-8601>
```

## Session Checkpointing

All phase transitions are checkpointed to `.claude/compound-state/<session-id>.yaml` enabling:

- **Resume**: Pick up where you left off after context loss
- **Audit**: Full trace of what happened in each phase
- **Metrics**: Track time and effort distribution across phases

### Checkpoint Schema

```yaml
session_id: string          # Unique session identifier
task: string                # Original task description
phase: string               # current phase: plan|work|review|compound|complete
plan_ref: string            # Path to plan file
review_ref: string          # Path to review report
commits: list               # Git commit SHAs produced
knowledge_entries: list     # Knowledge entry IDs created
findings_summary:           # Review findings count
  critical: int
  warning: int
  info: int
timestamp: string           # Last updated (ISO-8601)
created_at: string          # Session start (ISO-8601)
completed_at: string        # Session end (ISO-8601), null if in progress
```

## Usage Examples

### Full Loop
```
/compound "Add OAuth2 authentication to aceengineer-website"
```

### Phase-Specific
```
/compound plan "Add OAuth2 authentication"
/compound work
/compound review
/compound learn
```

### Resume
```
/compound resume flickering-rolling-rossum
```

## Integration Points

| Skill | Phase | Integration |
|-------|-------|-------------|
| knowledge-manager | Plan | `/knowledge advise` retrieves prior learnings |
| knowledge-manager | Compound | `/knowledge capture` stores new learnings |
| work-queue | Plan | Items with `compound: true` route here |
| core-planner | Plan | Delegates plan synthesis |
| core-coder | Work | Delegates TDD implementation |
| core-reviewer | Review | Delegates finding aggregation |
| skill-learner | Compound | Triggers if pattern score > 0.7 |
| claude-reflect | All | Daily reflection incorporates session data |

## What This Skill Does NOT Do

- Does not duplicate logic from delegated skills
- Does not execute shell scripts (orchestrates via Task tool)
- Does not modify existing skill behavior (additive only)
- Does not require new dependencies

## Version History

- **1.0.0** (2026-01-31): Initial release
