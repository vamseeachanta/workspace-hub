# Orchestrator-Worker Context Isolation

> Why separating planning from execution matters in AI-augmented engineering.
> Based on 12+ months of production multi-agent operation.

---

## The Problem: Context Overload

Single-agent sessions degrade predictably. When one agent plans, implements, reviews,
and ships in a single session, context windows fill with irrelevant detail. The original
plan gets fuzzy. The agent starts solving problems that do not exist.

### Measured Degradation Pattern

```
Single Agent Session (4+ hours)
├── Hour 1: Plans the feature (reads 15 files, creates plan)
│   Context window: 15% full, plan is clear
├── Hour 2: Starts implementing (debugging, reading more files)
│   Context window: 40% full, plan details start to truncate
├── Hour 3: Implements more (error loops, retries, tool calls accumulate)
│   Context window: 70% full, plan forgotten, working from code not spec
├── Hour 4: Reviews own work (reviews what was built, not what was planned)
│   Context window: 90% full, can't remember original requirements
└── Result: Drift between plan and implementation, self-review is rubber-stamp
```

This pattern repeats regardless of which AI agent runs the session. It is a property
of bounded context windows, not a property of any specific model.

### Why Self-Review Fails

An agent reviewing its own work is like a developer reviewing their own PR. They wrote
it, so it looks correct. The context that justified each decision is still in the
session. Blind spots are invisible precisely because they are the agent's blind spots.

---

## The Solution: Orchestrator + Workers

**Orchestrator**: Maintains the plan, delegates work, verifies results against spec.
**Workers**: Execute focused tasks with fresh context, return results.

```
Orchestrator Session
├── Reads requirements, creates plan
├── Designs worker prompts (each self-contained)
├── Spawns Worker 1 with plan section + relevant files only
├── Spawns Worker 2 with plan section + relevant files only
├── Collects results from both workers
├── Verifies each result against the original plan
└── Ships or sends back with specific feedback

Worker 1 Session (completely fresh context)
├── Receives: Plan section 2.1 + 3 relevant files
├── Implements only what the plan specifies
├── Runs tests to verify
└── Returns: Updated files + summary of what was done

Worker 2 Session (completely fresh context)
├── Receives: Plan section 2.2 + 4 relevant files
├── Implements only what the plan specifies
├── Runs tests to verify
└── Returns: Updated files + summary of what was done
```

### Why This Works

| Problem | Single Agent | Orchestrator-Worker |
|---------|-------------|-------------------|
| Context overload | Grows linearly with session length | Each worker starts fresh |
| Plan drift | Forgets the plan as context fills | Orchestrator maintains plan throughout |
| Parallel work | Sequential only | Workers run in parallel |
| Self-review bias | Same agent reviews its own work | Different agent reviews |
| Failure recovery | Must reconstruct lost context | Restart worker with same prompt |
| Session length | 4+ hours for complex features | 1-2 hours per worker |

---

## Production Implementation: Overnight Batch Dispatch

The most mature implementation of orchestrator-worker in this system is the overnight
batch dispatch pattern. The skill is documented at
`.claude/skills/software-development/overnight-parallel-agent-prompts/SKILL.md` (v1.2.0).

### How It Works

1. **Triage phase** (orchestrator): Claude reads open GitHub issues, categorizes by
   priority and domain, checks which issues have `status:plan-approved` labels.

2. **Prompt design** (orchestrator): Claude creates self-contained prompts for each
   terminal. Each prompt includes:
   - Full context (no references to "the issue" -- everything is inline)
   - Exact file paths to modify
   - Acceptance criteria
   - Commit message templates
   - Negative write boundaries (files this terminal must NOT touch)
   - Mandatory cross-review step at the end

3. **Contention map** (orchestrator): Before launching, the orchestrator produces a
   file ownership map:
   ```
   Terminal 1 writes: docs/assessments/, docs/roadmaps/
   Terminal 2 writes: scripts/quality/, tests/quality/
   Terminal 3 writes: scripts/analysis/, tests/analysis/
   Terminal 4 writes: docs/methodology/, docs/standards/
   Terminal 5 writes: scripts/cron/, tests/cron/
   Zero overlap confirmed.
   ```

4. **Launch** (operator): The user opens 5 terminals and launches each prompt using
   the tested unattended pattern:
   ```bash
   PROMPT=$(< docs/plans/overnight-prompts/2026-04-09/terminal-1-synthesis.md)
   claude -p \
     --permission-mode acceptEdits \
     --no-session-persistence \
     --output-format text \
     --max-budget-usd 20 \
     "$PROMPT" </dev/null | tee logs/claude-terminal-1.log
   ```

5. **Morning review** (orchestrator or user): Check deliverables, verify no git
   conflicts, review cross-review artifacts.

### Provider Allocation

Different AI providers have different strengths. The allocation pattern:

| Terminal | Provider | Best for |
|----------|----------|----------|
| 1 | Claude | High-context synthesis: architecture scanning, roadmaps, cross-file analysis |
| 2 | Codex seat 1 | Bounded TDD implementation: tests + paired source code |
| 3 | Codex seat 2 | More bounded TDD: test coverage uplift, package-level work |
| 4 | Gemini | Doc generation: staleness scanning, doc refresh, audit reports |
| 5 | Claude/Hermes | Pipeline/tool building: scripts with tests, integration work |

This allocation is not arbitrary. It emerged from observing which providers succeed at
which tasks across hundreds of overnight runs.

### Git Contention Avoidance

With 5 agents writing to the same repository simultaneously, git conflicts are
the primary failure mode. The contention avoidance rules:

1. **No two terminals touch the same file.** Period.
2. **No two terminals touch the same directory** if possible.
3. **Negative write boundaries** in each prompt: explicit lists of paths the terminal
   must NOT write to (owned by other terminals).
4. **`git pull origin main` before every push** in the prompt.
5. **Staggered commits** if directory overlap is unavoidable.

When these rules are followed, the overnight success rate is high. When they are
violated, `index.lock` errors and merge conflicts follow.

---

## Pattern Variants

### Variant 1: Subagent Delegation (Claude Code)

Claude Code's built-in subagent mechanism creates workers with fresh context:

```
claude (orchestrator)
  ├── subagent: "Implement phase 2: database schema"
  │   context: "Plan at .planning/phases/02-plan.md"
  │   tools: [terminal, file]
  ├── subagent: "Write tests for phase 2"
  │   context: "Spec at .planning/phases/02-plan.md, schema at schemas/v2.sql"
  │   tools: [terminal, file]
  └── orchestrator verifies results
```

### Variant 2: Worktree Isolation

For work that cannot share a single worktree:

```bash
# Each worker gets its own git worktree
git worktree add ../.claude/worktrees/worker-1 main
git worktree add ../.claude/worktrees/worker-2 main

# Workers operate in complete filesystem isolation
# Orchestrator reviews diffs from each worktree
```

This is the pattern used by the GSD framework (`/gsd:new-workspace`) and by
Claude Code's own worktree management
(`.claude/worktrees/agent-*` directories).

### Variant 3: Issue-Based Routing

GitHub issues serve as the work distribution mechanism:

```bash
# Issues labeled for specific agents
gh issue create --title "feat: mooring schema" --label "agent:codex,phase:2"
gh issue create --title "feat: riser validation" --label "agent:claude,phase:2"

# Each agent picks up issues matching its labels
# Cross-review happens on the resulting PRs
```

### Variant 4: Staged Cascade (Plan-Gated Repos)

For repositories with plan-approval enforcement (like workspace-hub), a 3-stage
cascade:

1. **Planning workers** (stage 1): Each writes one dossier/result file. No code changes.
2. **Conversion workers** (stage 2): Convert approved plans into execution packs.
3. **Ops workers** (stage 3): Generate exact `gh` commands and implementation prompts.

This cascade was developed for the 2026-04-09 10-session planning pack and refined
in the follow-up 4-session packs. It respects hard-stop workflow gates while
maximizing parallel throughput.

---

## Enforcement Requirements

Without enforcement, orchestrator-worker separation breaks down. Workers start
planning. Orchestrators start implementing. The boundary erodes.

Current enforcement:

| Gate | Script | What it enforces |
|------|--------|-----------------|
| Plan approval | `.claude/hooks/plan-approval-gate.sh` | Workers cannot write implementation code without approved plan marker |
| Cross-review | `.claude/hooks/cross-review-gate.sh` | PRs cannot be created without review evidence |
| Tool call ceiling | `.claude/hooks/session-governor-check.sh` | Sessions pause at 200 tool calls (prevents runaway workers) |
| TDD pairing | `scripts/enforcement/require-tdd-pairing.sh` | Warns when code changes lack paired tests |
| Review on push | `scripts/enforcement/require-review-on-push.sh` | Blocks push without review evidence (REVIEW_GATE_STRICT=1) |
| Artifact verification | `.claude/skills/coordination/artifact-verification/SKILL.md` | Orchestrator verifies worker outputs against plan before accepting |
| Discovery protocol | `.claude/skills/coordination/worker-discovery-protocol/SKILL.md` | Workers log discoveries; orchestrator triages and propagates |

These are registered in `.claude/settings.json` as PreToolUse hooks, so they fire
automatically on every tool call. No agent can bypass them by choosing a different
command path.

### Post-Execution Verification

After a worker returns results, the orchestrator runs the **artifact verification**
checklist (`.claude/skills/coordination/artifact-verification/SKILL.md`):
1. Scope alignment -- files changed match the plan
2. Acceptance criteria -- each AC satisfied with evidence
3. Test coverage -- tests match the plan's TDD test list
4. Artifact completeness -- all deliverables present
5. No unplanned side effects -- no unrelated changes

Verification markers are written to `.planning/verified/<issue>.md` with
PASS/PARTIAL/FAIL verdict.

### Knowledge Propagation

Workers log discoveries to `.planning/discoveries/YYYY-MM-DD-worker.jsonl` during
execution. At session end, the orchestrator triages each discovery and routes it to
the appropriate target (GitHub issue, SKILL.md, KNOWLEDGE.md, or discard). See
`.claude/skills/coordination/worker-discovery-protocol/SKILL.md` for details.

---

## Common Pitfalls

1. **Workers creating their own plans.** Defeats the purpose. Workers should receive
   plans, not create them. The plan-approval gate prevents this.

2. **Orchestrator implementing directly.** Context overload returns immediately. If
   the orchestrator starts coding, it stops being an orchestrator.

3. **No verification step.** The orchestrator must verify worker output against the
   plan, not trust it. Workers optimize for task completion, not plan adherence.

4. **Stale context in worker prompts.** Workers must get the current plan version.
   If the plan was updated after the prompt was written, the worker builds the wrong thing.

5. **Missing handoff documentation.** If a worker fails, the next worker must pick up
   from where the previous one left off. Session handoffs require explicit artifacts.

6. **Governance hooks blocking final writes.** In repos with tool-call ceilings, a
   worker may complete analysis but fail at the final file write. The session governor
   (`scripts/workflow/session_governor.py`) uses a three-tier verdict (CONTINUE/PAUSE/STOP)
   to manage this gracefully.

---

## Context Relief Metrics

| Metric | Single Agent | Orchestrator-Worker |
|--------|-------------|-------------------|
| Session length to complete feature | 4+ hours | 1-2 hours per worker |
| Context window usage | Grows linearly | Flat per worker |
| Plan drift | Frequent after hour 2 | Rare (orchestrator maintains plan) |
| Self-review effectiveness | Low (biased) | High (independent reviewer) |
| Parallel throughput | 1x | 3-5x (limited by terminals) |
| Overnight success rate | N/A | High with contention avoidance |

---

## Key Takeaway

Context isolation is not a nice-to-have. It is a prerequisite for reliable multi-hour
AI-assisted engineering. The orchestrator-worker pattern works because it converts one
hard problem (a single agent maintaining coherence over 4+ hours) into multiple easy
problems (workers executing focused tasks in 30-90 minutes each). Every production
AI workflow we run uses some variant of this pattern.

---

## Related

- [compound-engineering.md](compound-engineering.md) -- Lesson 2 overview
- [enforcement-over-instruction.md](enforcement-over-instruction.md) -- Why enforcement prevents boundary erosion
- [cross-review.md](cross-review.md) -- Independent review as a form of context isolation
- `.claude/skills/software-development/overnight-parallel-agent-prompts/SKILL.md` -- The production skill
- `.claude/skills/coordination/artifact-verification/SKILL.md` -- Orchestrator verification checklist (#2020)
- `.claude/skills/coordination/worker-discovery-protocol/SKILL.md` -- Worker knowledge propagation (#2020)
- `docs/governance/SESSION-GOVERNANCE.md` -- Session lifecycle checkpoints
- `docs/standards/SUBAGENT_CONTEXT_ISOLATION.md` -- Formal subagent isolation convention
