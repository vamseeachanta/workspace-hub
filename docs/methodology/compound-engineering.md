# Compound Engineering Methodology

> 5 operational lessons from running a production AI-augmented engineering firm

**Author:** Vamsee Achanta, P.E. (23yr exp)
**Firm:** ACE Engineer -- $120K/yr retainer target
**Status:** Operational since 2025-Q2, continuously improving
**Contact:** aceengineer.com

---

## Executive Summary

This is not theory. This is the actual methodology that runs 691+ skills across multiple agents (Claude, Codex, Gemini, Hermes) and multiple machines. The patterns below emerged from doing real engineering work -- not from designing them upfront.

### The Five Lessons

1. **Enforcement Over Instruction** -- text-based rules get bypassed. Technical gates don't.
2. **Orchestrator/Worker Separation** -- one agent with everything vs coordinator + isolated workers
3. **Compound Learning Loop** -- skills improve from real work, not upfront design
4. **Multi-Agent Parity** -- shared knowledge base eliminates redundant discovery
5. **3-Agent Cross-Review** -- independent reviewers for plans AND artifacts

---

## Lesson 1: Enforcement Over Instruction

### The Problem

Agents (Claude, Codex, Gemini, Hermes) consistently bypass review constraints over time. They act like humans who want to get work done and skip the hard parts. Current text-based instructions (CLAUDE.md, AGENTS.md, skills) are treated as suggestions, not gates.

### The Data

- Review compliance: **4%** (target: 80%)
- 22 unreviewed commits in 24 hours
- Zero REVIEWS.md files created despite active work

### What Doesn't Work

- "Always do X before Y" in CLAUDE.md
- Skills that describe a review process
- Polite reminders in prompts

### What Works

- Pre-commit hooks that check for plan approval markers
- Pre-push hooks that block unreviewed commits (REVIEW_GATE_STRICT=1)
- CI pipelines that reject PRs without review evidence
- Automatic compliance dashboards that flag violations

### The Rule

**If you can't enforce it technically, agents won't follow it.** Period.

---

## Lesson 2: Orchestrator/Worker Separation

### The Problem

Single agent handling everything leads to context overload. The agent loses the plan, forgets constraints, and produces inconsistent results across a multi-hour session.

### What Works

**Orchestrator pattern:** One agent maintains the plan, coordinates work, and verifies results. Workers execute focused tasks with fresh context.

```
Orchestrator (maintains plan, delegates, verifies)
  ├── Worker 1: Fresh context, focused on Task A
  ├── Worker 2: Fresh context, focused on Task B
  └── Worker 3: Fresh context, focused on Task C
```

### Benefits

- **Context relief**: Each worker gets a clean slate
- **Parallel execution**: Workers run simultaneously
- **Better quality**: Focused intent, not diluted attention
- **Verification**: Orchestrator checks worker output against spec

### Implementation

```bash
# Orchestrator creates plan
gh issue create --title "feat: ..."
# Workers get fresh context via subagents
delegate_task goal="Implement phase 2" context="Plan at .planning/phases/02-plan.md"
# Orchestrator verifies results
# If verification fails: worker gets specific feedback, tries again
```

### The Rule

**Separate planning from execution. The planner doesn't code. The coder doesn't plan.**

---

## Lesson 3: Compound Learning Loop

### The Problem

Learnings from one session are lost or require manual capture. The same mistakes are made again. Skills don't improve unless someone actively updates them.

### The Evolution Path

The progression from raw documents to self-improving systems:

```
PDFs → Filename Index → LLM Summary Index → LLM Knowledge Bases → Self-Improving Repo
```

### What Works

**Skills that improve from actual work, not upfront design.** When a task hits a pitfall, the system captures it automatically. Future tasks avoid the same pitfall.

```
Task executes → Pitfall encountered → Issue auto-created
  → Skill updated → Next task succeeds → Cycle continues
```

### Implementation

- Post-commit hooks that detect patterns worth capturing
- Skills that reference their own revision history
- Knowledge bases that grow from real engineering work
- Cross-agent memory bridges so all agents benefit from one agent's learning

### The Rule

**Every failure is a skill update waiting to happen. Automate the capture.**

---

## Lesson 4: Multi-Agent Parity

### The Problem

Claude Code "has been loitering in these details more than anyone else" and has more prepared skills. When setting up a new agent (Gemini, fresh Claude Code), you have to go through the same learning curve from scratch.

### What Works

**Shared knowledge base, single source of truth.** All agents read from the same `.claude/skills/` directory. Skills are in the repo, not in agent memory.

```
.claude/skills/ (git repository)
  ├── claude reads from here
  ├── codex reads from here  
  ├── gemini reads from here
  └── hermes reads from here (symlink)
```

### The Secret Sauce

1. Skills are the primary knowledge carrier (not agent memory)
2. Skills move to repo hub with symlinks for agents
3. Memory consolidates into repo-tracked files
4. Everything is git-committed immediately

### The Rule

**If knowledge lives in an agent's memory session, it's lost when the session ends. Put it in the repo.**

---

## Lesson 5: 3-Agent Cross-Review

### The Problem

A single agent reviewing its own work misses blind spots. Even a careful agent cannot catch everything it would have done differently.

### What Works

**Three independent agents (Claude, Codex, Gemini) review each other's plans AND artifacts.** Running for 1 year before "adversarial" became the standard term.

```
Claude creates plan
  ↓
Codex reviews plan → finds issues → Claude updates
  ↓
Gemini reviews plan → finds more issues → Claude updates
  ↓
Plan approved → Implementation begins
  ↓
Codex implements
  ↓
Claude reviews artifact → Gemini reviews artifact
  ↓
All reviewers approve → Ship
```

### Why It Works

- **Different blind spots**: Each agent has different biases
- **Cross-pollination**: Reviewers learn from what they review
- **Quality floor**: No single point of failure
- **Evidence trail**: Every review leaves a record

### The Rule

**No artifact ships without at least 2 independent reviewers. Plans need 3.**

---

## Implementation Reference

### File Structure

```
workspace-hub/
├── .claude/
│   ├── hooks/
│   │   └── cross-review-gate.sh      # Claude PreToolUse hook
│   └── settings.json                  # Hook configuration
├── .git/hooks/
│   ├── pre-commit                     # Plan gate (NEW)
│   └── pre-push.sh                    # Review gate + CI checks
├── scripts/enforcement/
│   ├── require-plan-approval.sh       # NEW: Plan gate script
│   ├── require-review-on-push.sh      # Push-time review check
│   ├── require-cross-review.sh        # PR creation gate
│   ├── require-tdd-pairing.sh         # Test enforcement
│   ├── compliance-dashboard.sh        # NEW: Compliance reporting
│   └── upgrade-enforcement.sh         # NEW: Advisory → strict
├── .planning/
│   ├── phases/
│   │   └── */REVIEWS.md              # Review evidence
│   ├── plan-approved/                 # Plan approval markers
│   └── STATE.md                       # Current phase
└── logs/
    ├── hooks/
    │   ├── plan-gate-events.jsonl     # Plan gate log
    │   └── review-gate-bypass.jsonl   # Bypass audit
    └── compliance/
        └── compliance-YYYYMMDD.json   # Daily reports
```

### Enforcement Levels

| Level | Type | Example | Blocking? |
|-------|------|---------|-----------|
| 1 | Text instructions | CLAUDE.md, AGENTS.md | No |
| 2 | Advisory scripts | Scripts that print warnings | No |
| 3 | Hard gates | Pre-commit hook with `exit 1` | Yes |
| 4 | CI enforcement | GitHub Actions rejecting PRs | Yes |

**Current state**: Level 2 (advisory) for most things, Level 3 partially implemented.
**Target state**: Level 3 for plan gate (immediate), Level 4 for review gate (next).

---

## Metrics That Matter

| Metric | Current | Target | Where to Check |
|--------|---------|--------|----------------|
| Review compliance | 4% | 80%+ | #2012, compliance-dashboard.sh |
| Plan approval rate | unknown | 90%+ | plan-gate-events.jsonl |
| Skill updates/month | unknown | 20+ | .claude/skills/ git history |
| Cross-review coverage | partial | 100% | .planning/phases/*/REVIEWS.md |
| Bypass attempts | unknown | trending down | logs/hooks/review-gate-bypass.jsonl |

---

## For Clients

This methodology is available for consulting engagements through [aceengineer.com](https://aceengineer.com). ACE Engineer provides core engineering services with the same discipline:

- **OrcaFlex** mooring and riser analysis
- **Finite Element Analysis** for offshore structures
- **Cathodic Protection** design per DNV/ISO
- **API 579** Fitness-for-Service assessments
- **Python automation** for engineering workflows

The methodology documented here is a subset of how ACE approaches all engineering work: systematic, reviewed, enforced, continuously improving.

---

## Related GitHub Issues

- #1876 -- Enforce engineering workflow via Hermes prefill + Claude Code hooks
- #1760 -- Self-improvement commands (/compound, /reflect, /knowledge)
- #112 -- Cowork relevance and multi-agent ecosystem fit
- #1962 -- Tier-1 repo ecosystem refactoring
- #2017 -- Agent bypass resistance enforcement
- #2018 -- Orchestrator/worker context enforcement
- #2020 -- Publish knowledge as aceengineer.com content
