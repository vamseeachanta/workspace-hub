# Orchestrator-Worker Context Isolation

> Why separating planning from execution matters in AI-augmented engineering

## The Problem

Single agent context overload. When one agent plans, implements, reviews, and ships in one session, it loses the plan mid-way through. Context windows fill with irrelevant details. The original intent gets fuzzy.

### What Happens Without Separation

```
Single Agent Session (4+ hours)
├── Hour 1: Plans the feature (reads 15 files, creates plan)
├── Hour 2: Starts implementing (context window 40% full)
├── Hour 3: Implements more (context window 70% full, plan details truncated)
├── Hour 4: Reviews own work (plan forgotten, reviews against what was built, not what was planned)
└── Result: Drift between plan and implementation
```

## The Solution

**Orchestrator** maintains the plan, delegates work, and verifies results.
**Workers** execute focused tasks with fresh context.

```
Orchestrator Session
├── Reads requirements and creates plan
├── Spawns Worker 1 with plan + focused context
├── Spawns Worker 2 with plan + focused context
├── Collects results, verifies against plan
└── Ships or sends back for revision

Worker 1 Session (fresh context)
├── Receives: Plan section 2.1 + relevant files
├── Implements only what's in the plan
└── Returns: Updated files + summary

Worker 2 Session (fresh context)
├── Receives: Plan section 2.2 + relevant files
├── Implements only what's in the plan
└── Returns: Updated files + summary
```

## Why This Works

| Problem | Single Agent | Orchestrator-Worker |
|---------|-------------|-------------------|
| Context overload | Yes (accumulates) | No (each worker starts fresh) |
| Plan drift | Yes (forgets the plan) | No (orchestrator maintains it) |
| Parallel work | No (sequential) | Yes (workers run in parallel) |
| Self-review bias | Yes (same agent) | No (different reviewer) |
| Failure recovery | Poor (lost context) | Good (restart worker with same context) |

## Implementation Patterns

### Pattern 1: Subagent Delegation (Hermes delegate_task)

```python
# Orchestrator launches workers
delegate_task(
    goal="Implement phase 2: database schema",
    context="Plan: .planning/phases/02-plan.md, existing schema: schemas/v1.sql",
    toolsets=["terminal", "file"]
)
```

### Pattern 2: GitHub Issue Routing (Multi-Agent)

```bash
# Issue created with labels routing to specific agents
gh issue create \
  --title "feat: database schema for mooring analysis" \
  --label "cat:engineering,agent:claude,phase:2"

# Each agent picks up issues matching its label
# Orchestrator verifies via cross-review
```

### Pattern 3: Worktree Isolation (Claude Code)

```bash
# Each worker gets its own worktree
git worktree add ../work-worker-1 main
git worktree add ../work-worker-2 main

# Workers operate in isolation, orchestrator reviews diffs
```

## Context Relief Metrics

Measure the benefit:

| Metric | Before | After |
|--------|--------|-------|
| Session length to complete feature | 4+ hours | 1-2 hours |
| Prompt tokens (context window usage) | Grows linearly | Flat per worker |
| Plan drift (deviation from spec) | Frequent | Rare |
| Self-review effectiveness | Low (biased) | High (independent) |

## Enforcement Requirements

Without enforcement, orchestrator/worker separation breaks down:

1. **Workers must not plan** -- they receive plans, don't create them
2. **Workers must not skip verification** -- they report evidence against the plan
3. **Orchestrator must not implement** -- it delegates, not codes
4. **All handoffs must be documented** -- plan artifacts go to workers, results return

This is enforced via:
- `require-plan-approval.sh` -- workers can't commit without plan that orchestrator approved
- `cross-review-gate.sh` -- PRs can't be created without cross-review evidence
- `PRECOMMIT` hook -- blocks plan-less commits

## Common Pitfalls

1. **Workers creating their own plans** -- defeats the purpose. Workers should implement, not plan.
2. **Orchestrator implementing directly** -- context overload returns. Delegate or die.
3. **No verification step** -- orchestrator must verify worker output, not trust it.
4. **Stale context** -- workers must get current plan version, not stale copies.
5. **Missing handoff docs** -- if a worker fails, the next must pick up from where the previous left off.

## Related

- docs/methodology/compound-engineering.md (Lesson 2: Orchestrator/Worker Separation)
- docs/methodology/enforcement-over-instruction.md (why enforcement is needed)
- .git/hooks/pre-commit (prevents worker plan creation)
- .claude/hooks/cross-review-gate.sh (prevents unverified work)
