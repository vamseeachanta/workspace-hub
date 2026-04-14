# Compound Engineering Methodology

> 5 operational lessons from running a production AI-augmented engineering firm.
> Everything documented here is deployed and running. No theory.

**Context:** ACE Engineer consulting (aceengineer.com) -- Professional Engineering firm
running multi-agent AI workflows in production since 2025-Q2. 691+ skills, 4 AI agents
(Claude, Codex, Gemini, Hermes), 2 machines (ace-linux-1, licensed-win-1), serving
offshore engineering clients.

---

## What Compound Engineering Actually Means

Compound engineering is the practice where every completed task makes the next task
easier, faster, and more reliable. This is not a metaphor. It is a measurable property
of the system.

When a session encounters a problem -- say, an OrcaWave API returning frequencies in
Hz descending order instead of the expected ascending rad/s -- the fix does not stay in
that session. It gets captured into a skill file (`.claude/skills/engineering/orcawave/`),
committed to git, and is immediately available to every agent on every machine. The next
session that touches OrcaWave never hits the same problem.

The concrete loop:

```
Work session encounters pitfall
    --> Pitfall is documented in a skill or KNOWLEDGE.md
        --> Git commit makes it available to all agents
            --> Next session avoids the pitfall
                --> Saved time is reinvested in new work
                    --> New work encounters new pitfalls
                        --> Cycle continues
```

After 12+ months of operation, the compound effect is substantial:
- 691+ skills spanning 48 categories cover most recurring patterns
- Nightly learning pipelines (`scripts/cron/comprehensive-learning-nightly.sh`) automatically
  extract session learnings, sync agent memories, and validate skill health
- Cross-agent memory bridges (`scripts/cron/sync-agent-memories.sh`) ensure that what
  Hermes learns, Claude, Codex, and Gemini all know by the next session

### What the System Looked Like Before

In early 2025, the workflow was:
- Single agent (Claude) with manual prompts
- No skill files -- all knowledge in session memory (lost on session end)
- No enforcement -- review, planning, and TDD were aspirational
- Each session started from scratch

### What It Looks Like Now

```
workspace-hub/
├── .claude/
│   ├── skills/              # 691+ skills across 48 categories
│   ├── hooks/               # 28 enforcement hooks (PreToolUse, PostToolUse)
│   ├── memory/              # Git-tracked cross-machine memory
│   │   ├── context.md       # Machine conventions, paths
│   │   ├── agents.md        # User profile, workflow rules
│   │   ├── KNOWLEDGE.md     # Engineering lessons, tool quirks
│   │   └── topics/          # Auto-memory topic files
│   └── settings.json        # Hook configuration, env vars
├── scripts/
│   ├── enforcement/         # 12 enforcement scripts
│   ├── cron/                # 30+ nightly automation scripts
│   ├── workflow/            # Session governor, governance checkpoints
│   └── memory/              # Memory bridge scripts
├── AGENTS.md                # Multi-agent parity config
└── docs/
    ├── governance/          # SESSION-GOVERNANCE.md, TRUST-ARCHITECTURE.md
    ├── standards/           # AI_REVIEW_ROUTING_POLICY.md, HARD-STOP-POLICY.md
    └── methodology/         # These documents
```

---

## The Five Lessons

Each lesson is documented in its own file with implementation details. This section
provides the executive summary and explains how they interconnect.

### Lesson 1: Enforcement Over Instruction

**File:** [enforcement-over-instruction.md](enforcement-over-instruction.md)

Text-based rules get bypassed. We measured 4% review compliance when relying on
CLAUDE.md and AGENTS.md instructions alone. Technical enforcement -- pre-commit hooks,
PreToolUse gates, CI checks -- achieves near 100% compliance on enforced gates.

The enforcement gradient from `.claude/rules/patterns.md`:

| Level | Mechanism | Reliability | Example |
|-------|-----------|-------------|---------|
| 0 | Prose (CLAUDE.md) | Lowest | "Always review before committing" |
| 1 | Micro-skill | Medium | Stage-specific checklists loaded at entry |
| 2 | Script | High | `scripts/enforcement/require-review-on-push.sh` |
| 3 | Hook | Strongest | `.claude/hooks/plan-approval-gate.sh` |

The practical lesson: **if you can express a rule as `exit 0` / `exit 1`, write a script.
If it must fire on every commit, promote it to a hook.**

### Lesson 2: Orchestrator-Worker Separation

**File:** [orchestrator-worker.md](orchestrator-worker.md)

Single-agent sessions degrade after 2+ hours. Context windows fill, the plan gets
fuzzy, and the agent starts solving problems that don't exist. The solution: one agent
maintains the plan and delegates; workers execute in fresh-context isolation.

Production implementation: 5 parallel overnight terminals, each with a different
AI provider, working on file-disjoint tasks. The orchestrator (Claude) designs the
prompts; workers (Codex seats 1-2, Gemini, Claude workers) execute them. Worktree
isolation ensures no git contention. The skill that manages this is at
`.claude/skills/software-development/overnight-parallel-agent-prompts/SKILL.md`.

### Lesson 3: Compound Learning Loop

The core mechanism of compound engineering. Every session writes to the shared
knowledge base:

1. **Skill updates**: When a pitfall is encountered, the relevant skill file gets
   a new pitfall entry. 220+ pitfalls are now documented across the SKILL.md files.

2. **KNOWLEDGE.md**: Cross-cutting engineering lessons (95 lines, 200-line limit)
   covering tool quirks, debugging protocols, git patterns, and shell portability.

3. **Nightly pipeline**: `scripts/cron/comprehensive-learning-nightly.sh` runs a
   12-step learning extraction pipeline every night:
   - Pull latest state from all machines
   - rsync raw sessions from ace-linux-2 and licensed-win-1
   - Export Hermes and Codex session logs
   - Sync agent memories cross-agent
   - Validate skill frontmatter
   - Run skill curation
   - Check test health
   - Track provider costs
   - Rebuild specs index
   - Scan for drift in Codex and Hermes sessions
   - Commit all learning artifacts back to git

4. **Memory bridges**: `scripts/memory/bridge-hermes-claude.sh` syncs Hermes
   memory into `.claude/memory/agents.md` (git-tracked), so every `git pull` on any
   machine gets updated context.

### Lesson 4: Multi-Agent Parity

**File:** [multi-agent-parity.md](multi-agent-parity.md)

$269/month across 4 AI subscriptions (Claude Max $200, Codex x2 $40, Gemini $19.99).
Context parity mandate: corrections in one agent sync to ALL others. Zero waste.

The mechanism: `.claude/skills/` is the single source of truth. All agents read from
it. Hermes accesses it via `external_dirs` configuration. New skills go to the repo,
not to `~/.hermes/skills/`. The WRITE-BACK RULE (#1941) enforces this.

Git is the sync mechanism. No proprietary sync protocol. `git pull` on any machine
gets the latest skills, knowledge, and memory.

### Lesson 5: 3-Agent Cross-Review

**File:** [cross-review.md](cross-review.md)

Three independent agents (Claude, Codex, Gemini) review every plan AND every artifact.
This is not optional -- it's enforced at Level 3 (Hook) via
`.claude/hooks/cross-review-gate.sh`, which blocks PR creation without review evidence.

The routing policy (`docs/standards/AI_REVIEW_ROUTING_POLICY.md`) defines roles:
- **Claude**: orchestrator -- frames work, sequences execution, synthesizes reviews
- **Codex**: implementation worker and adversarial reviewer
- **Gemini**: adversarial reviewer for architecture and high-stakes synthesis

Each reviewer catches different failure modes. In practice, Codex is better at
catching implementation bugs; Gemini catches architectural drift; Claude catches
scope creep.

---

## How the Five Lessons Connect

These are not independent practices. They form a reinforcing system:

```
Enforcement (L1)     ensures    Cross-Review (L5) actually happens
Cross-Review (L5)    generates  learnings captured by the Compound Loop (L3)
Compound Loop (L3)   improves   Skills used by all agents via Parity (L4)
Parity (L4)          enables    Workers to operate with full context (L2)
Workers (L2)         execute    work that Enforcement (L1) gates
```

Remove any one, and the others degrade:
- Without enforcement, reviews get skipped
- Without reviews, quality drops and learnings are shallow
- Without the learning loop, skills stagnate
- Without parity, only one agent improves
- Without workers, context overload prevents focused execution

---

## Metrics That Matter

| Metric | Current | Target | Source |
|--------|---------|--------|--------|
| Skills in production | 691+ | Growing | `.claude/skills/` git history |
| Enforcement hooks active | 28 | Expanding | `.claude/hooks/` directory |
| Governance checkpoints | 7 | 7 | `scripts/workflow/governance-checkpoints.yaml` |
| Nightly pipeline steps | 12 | 15+ | `scripts/cron/comprehensive-learning-nightly.sh` |
| AI subscription cost | $269/mo | $269/mo | `AGENTS.md` |
| Cross-review gate | Level 3 (Hook) | Level 3 | `AI_REVIEW_ROUTING_POLICY.md` |
| Plan approval gate | Level 3 (Hook) | Level 3 | `plan-approval-gate.sh` |
| Tool call ceiling | 200/session | 200 | `governance-checkpoints.yaml` |

---

## For Technical Evaluators

If you are evaluating AI-assisted engineering workflows, the key differentiators
of this system are:

1. **Enforcement is technical, not textual.** Rules that can be bypassed are not rules.
2. **Skills are in the repo.** Not in agent memory, not in a proprietary database.
3. **Multiple agents work in parallel.** Not as a novelty, but as a production pattern.
4. **Everything is git-tracked.** Skills, knowledge, memory, enforcement config, hooks.
5. **The system improves itself.** Nightly pipelines capture, validate, and propagate learnings.

---

## Related Issues

- #1839 -- Session governance hard-stop checkpoints
- #1876 -- Enforce engineering workflow via hooks
- #1760 -- Self-improvement commands (/compound, /reflect, /knowledge)
- #1515 -- AI review routing policy
- #1537 -- Cross-review enforcement
- #1941 -- WRITE-BACK RULE for skill registration
- #2017 -- Agent bypass resistance enforcement
- #2018 -- Orchestrator/worker context enforcement
- #2021 -- This methodology documentation

## Key Takeaway

Compound engineering is not about having the best AI agent. It is about building a
system where every session -- regardless of which agent runs it -- leaves the system
better than it found it. The five lessons are the operational primitives that make
this work. They were not designed upfront; they emerged from doing real engineering
work with AI agents for over a year.
