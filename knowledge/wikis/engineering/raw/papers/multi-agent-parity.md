# Multi-Agent Parity

> How 4 AI agents share knowledge without redundant discovery.
> Based on running Claude, Codex, Gemini, and Hermes in production simultaneously.

---

## The Problem: Knowledge Silos

When you use multiple AI agents, each one discovers things independently. Claude
learns that OrcaWave returns frequencies in Hz descending order. Codex figures out
that `uv run` is required on Linux. Gemini discovers the correct commit message
convention. None of this transfers automatically.

### Why This Is Expensive

```
Claude spends 20 minutes learning the .gitignore structure     --> solves it
Codex encounters the same .gitignore confusion next session    --> solves it again
Gemini never encountered it                                    --> will spend 20 minutes next time
Hermes hit it a month ago but the fix is in ~/.hermes/memory/  --> invisible to the others
```

With 4 agents at $269/month total (Claude Max $200, Codex x2 $40, Gemini $19.99),
redundant discovery is a direct waste of subscription budget. The user directive is
explicit: **"corrections in one agent sync to ALL others. Zero waste."**

### The Anti-Patterns

| Anti-pattern | What happens | Cost |
|-------------|-------------|------|
| Knowledge in session memory only | Lost when session ends | Rediscovery every session |
| Skills only in `~/.hermes/skills/` | Only Hermes sees them | Other 3 agents rediscover |
| Agent memory stores facts locally | `~/.claude/projects/.../memory/` is Claude-only | Codex, Gemini never see it |
| Corrections spoken but not written | "Always use uv run" stays in conversation | Every new session starts ignorant |

---

## The Solution: Repository as Single Source of Truth

All agent knowledge lives in the git repository. Not in agent-specific memory. Not
in a proprietary sync service. In git-tracked files that every agent reads.

### Architecture

```
workspace-hub/                              (git repository)
├── .claude/
│   ├── skills/                             (691+ skills, 48 categories)
│   │   ├── engineering/                    (OrcaFlex, mooring, riser, FEA)
│   │   ├── software-development/           (overnight prompts, TDD, debugging)
│   │   ├── coordination/                   (issue planning, routing)
│   │   ├── email/                          (Gmail triage, drafting)
│   │   └── ... (48 total categories)
│   ├── memory/                             (git-tracked cross-machine memory)
│   │   ├── context.md                      (machine conventions, paths)
│   │   ├── agents.md                       (user profile, workflow rules)
│   │   ├── KNOWLEDGE.md                    (engineering lessons, tool quirks)
│   │   └── topics/                         (auto-memory topic files)
│   ├── hooks/                              (28 enforcement hooks)
│   ├── rules/                              (coding-style.md, patterns.md)
│   └── settings.json                       (hook config, env vars)
├── AGENTS.md                               (multi-agent conventions, 86 lines)
├── CLAUDE.md                               (Claude-specific context, 20 lines)
└── docs/
    ├── standards/                           (AI_REVIEW_ROUTING_POLICY.md)
    └── governance/                          (SESSION-GOVERNANCE.md)
```

### How Each Agent Reads Shared Knowledge

| Agent | Primary access | Config mechanism | Reads from |
|-------|---------------|-----------------|------------|
| Claude Code | Direct file access | Built-in `.claude/` support | `.claude/skills/`, `.claude/memory/`, `AGENTS.md` |
| Codex CLI | File access via `.codex/` adapter | `.codex/` thin adapter references `.claude/` | `.claude/skills/`, `AGENTS.md` |
| Gemini CLI | File access via `.gemini/` adapter | `.gemini/` thin adapter references `.claude/` | `.claude/skills/`, `AGENTS.md` |
| Hermes | Symlink via `external_dirs` | `external_dirs` in Hermes config includes `.claude/skills/` | `.claude/skills/` (via symlink), `~/.hermes/memories/` |

### The WRITE-BACK RULE (#1941)

This is the single most important convention for parity:

> **New skills and scripts go DIRECTLY to `workspace-hub/.claude/skills/` (NOT
> `~/.hermes/skills/`).** The repo is the source of truth. `external_dirs` includes
> `.claude/skills/` so both Hermes and Claude Code see everything. Everything is
> git-tracked. `~/.hermes/skills/` is only for personal/offline-only stuff.
> All `.claude/` writes are git-committed immediately.

Before this rule, Hermes accumulated skills in `~/.hermes/skills/` that no other
agent could see. After this rule, all skills go to the repo and all agents see
them immediately.

---

## The Memory Sync Model

Memory travels with the repository via git. No Hermes needed on Windows. No
proprietary sync protocol. `git pull` on any machine gets the latest everything.

### The Sync Flow

```
1. Hermes (ace-linux-1) writes memory to ~/.hermes/memories/
       |
2. Bridge script (scripts/memory/bridge-hermes-claude.sh) runs:
   - Reads Hermes memory
   - Extracts canonical facts
   - Injects into .claude/memory/agents.md (BRIDGE:START/END markers)
   - Mirrors Claude auto-memory topic files to topics/
   - Commits and pushes to git
       |
3. Any machine doing git pull gets updated .claude/memory/ automatically
       |
4. Windows (licensed-win-1): git pull --> has full context, no Hermes needed
       |
5. Return enrichment: new lessons on any machine go into KNOWLEDGE.md
   or topic files, committed and pushed. Next git pull propagates everywhere.
```

### Bridge Script Details

`scripts/memory/bridge-hermes-claude.sh` (issue #1886, #1890, #1892, #1893):

- Reads `~/.hermes/memories/MEMORY.md` and `~/.hermes/memories/USER.md`
- Extracts environment facts, conventions, project knowledge, user preferences
- Injects between `<!-- BRIDGE:START -->` and `<!-- BRIDGE:END -->` markers in
  `.claude/memory/agents.md`
- Deduplicates entries to prevent bloat (#1892)
- Mirrors Claude auto-memory topic files to `topics/` (#1893)
- Runs via cron (nightly) or on-demand

### Cross-Agent Memory Sync

`scripts/cron/sync-agent-memories.sh` provides deeper sync:

- Reads Hermes MEMORY.md and USER.md (section-separated entries)
- Categorizes entries: environment_facts, conventions, project_knowledge, user_preferences
- Writes structured YAML to `.claude/state/hermes-insights.yaml`
- Merges with Claude project memory to produce `.claude/state/cross-agent-memory.yaml`
- Idempotent: computes content hash, skips if sources unchanged

---

## Context Parity in Practice

### Example: The "uv run" Convention

1. User corrects Claude: "Always use `uv run`, not `python3`"
2. Claude updates `.claude/memory/context.md`: "Python Command Rule: Linux: ALWAYS
   `uv run` -- never bare `python3` or `pip`"
3. Git commits the change
4. Next Codex session starts, reads `.claude/memory/context.md`, uses `uv run`
5. Next Gemini session starts, reads same file, uses `uv run`
6. Hermes sees it via bridge sync on next nightly run

Time from correction to universal adoption: next `git pull` (seconds to hours,
depending on when the next session starts).

### Example: The OrcaWave Frequency Bug

1. Engineering session discovers OrcaWave returns Hz in descending order
2. Lesson captured in `.claude/memory/KNOWLEDGE.md`:
   "`.frequencies` returns Hz (not rad/s) in descending order"
3. Also captured in `.claude/skills/engineering/orcawave/` SKILL.md pitfalls section
4. All agents now know this before starting any OrcaWave work
5. No engineering session will make this mistake again

### Example: The Shebang Problem

1. Hermes shebang keeps reverting to `#!/usr/bin/env python3` (resolves to miniforge3,
   which lacks hermes deps)
2. Correct shebang: `/home/vamsee/.hermes/hermes-agent/.venv/bin/python`
3. Documented in `.claude/memory/agents.md` (via bridge)
4. Problem recurred 3 times before being captured -- now zero recurrences
5. Listed in agents.md Environment Facts so every agent sees it

---

## The Skill Sharing Architecture

Skills are the primary knowledge carrier. Not agent memory, not conversation context,
not documentation. Skills.

### Why Skills Over Memory

| Carrier | Persistence | Discoverability | Agent reach | Actionability |
|---------|------------|-----------------|-------------|---------------|
| Session memory | Session only | Low (agent must recall) | 1 agent | Medium |
| Agent auto-memory | Cross-session for that agent | Medium | 1 agent | Medium |
| KNOWLEDGE.md | Permanent (git) | High (loaded on start) | All agents | Medium |
| Skill file | Permanent (git) | Highest (loaded by name) | All agents | Highest |
| Documentation | Permanent (git) | Low (must be searched) | All agents | Low |

Skills win because they are:
- **Structured**: YAML frontmatter (name, description, version, tags, related_skills)
- **Discoverable**: `/skills` lists all available skills by category
- **Actionable**: Include step-by-step procedures, not just facts
- **Versionable**: Git history shows how the skill evolved
- **Testable**: Skill evals can verify the skill produces correct output

### Skill Count by Category (Top 10)

| Category | Count | Examples |
|----------|-------|---------|
| engineering | 50+ | OrcaFlex modeling, riser analysis, mooring design |
| software-development | 40+ | Overnight prompts, TDD, debugging, code review |
| coordination | 30+ | Issue planning, routing, agent dispatch |
| email | 25+ | Gmail triage, drafting, digest |
| data | 20+ | Pipeline, transformation, validation |
| github | 15+ | PR management, issue triage, release |
| research | 15+ | Nightly researchers, literature review |
| automation | 12+ | Cron, self-healing, workflow |
| finance | 10+ | Tax planning, portfolio signals |
| devops | 10+ | CI/CD, deployment, monitoring |

### Hermes Routing Configuration

Hermes accesses repo skills via `external_dirs` in its configuration:

```yaml
# ~/.hermes/config/config.yaml (excerpt)
external_dirs:
  - /mnt/local-analysis/workspace-hub/.claude/skills
```

This means Hermes's 691+ skill count includes both its native skills (`~/.hermes/skills/`)
and the repo skills (`.claude/skills/`). The WRITE-BACK RULE ensures new skills go
to the repo, not to `~/.hermes/skills/`, so all agents benefit.

---

## Cross-Machine Parity

The system runs across two machines:

| Machine | OS | Hermes | Python | Workspace |
|---------|-----|--------|--------|-----------|
| ace-linux-1 | Linux | Yes | `uv run` | `/mnt/local-analysis/workspace-hub` |
| licensed-win-1 | Windows | No | `python` | `D:\workspace-hub` |

### How Windows Gets Parity Without Hermes

1. All skills, memory, and knowledge are in the git repository
2. `git pull` on Windows gets everything
3. Claude Code on Windows reads `.claude/` directly
4. Codex on Windows reads via `.codex/` adapter
5. No Hermes needed -- the repo IS the shared brain

The only difference: Windows uses `python` instead of `uv run`. This is documented
in `.claude/memory/context.md` under "Python Command Rule" and every agent respects
it based on which machine it is running on.

---

## The Nightly Parity Pipeline

Three cron jobs maintain parity automatically:

### 1. Comprehensive Learning Nightly
**Script:** `scripts/cron/comprehensive-learning-nightly.sh`

12-step pipeline that runs every night:
- Pulls latest state from git
- rsyncs raw sessions from all machines
- Exports Hermes and Codex session logs
- Runs memory sync
- Validates skill health
- Commits learning artifacts back to git

### 2. Memory Bridge
**Script:** `scripts/memory/bridge-hermes-claude.sh`

Syncs Hermes memory into `.claude/memory/agents.md`:
- Reads `~/.hermes/memories/MEMORY.md` and `USER.md`
- Extracts facts, deduplicates, injects into BRIDGE markers
- Mirrors topic files
- Scores sync quality (target: 95+)

### 3. Agent Memory Sync
**Script:** `scripts/cron/sync-agent-memories.sh`

Deeper cross-pollination:
- Categorizes Hermes entries (env, conventions, project, user)
- Produces structured YAML (`hermes-insights.yaml`, `cross-agent-memory.yaml`)
- Merges with Claude project memory for unified index
- Idempotent via content hashing

---

## What Breaks Parity (and How to Fix It)

| Breakage | Symptom | Fix |
|----------|---------|-----|
| Knowledge in session memory only | Agent learns something, next session does not know | Write to `.claude/memory/` or skill file, commit |
| Skills in `~/.hermes/skills/` only | Only Hermes benefits | Move to `.claude/skills/`, update WRITE-BACK RULE |
| Agent auto-memory diverges | Claude "knows" things Codex does not | Bridge script syncs; manual check with `/compound-extended` |
| Stale git on Windows | Windows agent uses old skills | `git pull` before starting work |
| Bridge script fails silently | Hermes memory not propagated | Nightly cron logs, check `cron.log` |

---

## The Parity Checklist

For evaluators or new team members:

- [ ] All agents read from `.claude/skills/` (not agent-specific skill stores)
- [ ] No agent stores critical knowledge outside the repo
- [ ] New skills go to `.claude/skills/` immediately (WRITE-BACK RULE)
- [ ] User corrections trigger file updates, not just session acknowledgment
- [ ] Memory bridge runs on schedule (nightly cron)
- [ ] `AGENTS.md` has current agent subscription and role information
- [ ] `.claude/memory/agents.md` BRIDGE section has recent sync timestamp
- [ ] Cross-agent memory YAML is being generated (`hermes-insights.yaml`)

---

## Key Takeaway

Multi-agent parity is not about making all agents identical. It is about ensuring
that no agent operates with less context than any other. When Claude discovers that
OrcaWave frequencies come in Hz descending, and that fact gets committed to
`.claude/memory/KNOWLEDGE.md`, then every agent -- Claude, Codex, Gemini, Hermes,
on any machine -- knows it from the next session forward.

The mechanism is deliberately simple: git-tracked files in a shared directory
structure. No proprietary sync protocol, no agent-specific memory databases, no
cloud sync service. Git is the sync mechanism. The repository is the shared brain.

---

## Related

- [compound-engineering.md](compound-engineering.md) -- Lesson 4 overview
- [cross-review.md](cross-review.md) -- How parity enables effective cross-review
- `AGENTS.md` -- Multi-agent conventions and subscription details
- `.claude/memory/` -- The shared memory directory
- `scripts/memory/bridge-hermes-claude.sh` -- Memory bridge script
- `scripts/cron/sync-agent-memories.sh` -- Cross-agent memory sync
- `scripts/cron/comprehensive-learning-nightly.sh` -- Nightly parity pipeline
- #1760 -- Self-improvement commands (Phase 5: cross-agent bridge)
- #1886 -- Memory bridge implementation
- #1941 -- WRITE-BACK RULE
- #112 -- Cowork relevance and multi-agent ecosystem fit
