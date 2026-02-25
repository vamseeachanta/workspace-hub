---
name: skills-curation
description: Periodic skills library maintenance — online research for new/stale skills, knowledge graph review against active WRK items, session-input health check, and autonomous skill creation or WRK spin-off for deep gaps.
version: 1.0.0
category: workspace-hub
type: skill
trigger: scheduled
cadence: dynamic  # starts weekly; auto-adjusts based on signal yield
auto_execute: true
standing: true
capabilities:
  - online_research
  - knowledge_graph_review
  - gap_triage
  - skill_stub_creation
  - wrk_item_creation
  - session_input_health_check
  - yield_tracking
  - cadence_adjustment
tools: [Read, Write, Edit, Bash, Grep, Glob, WebSearch, Task]
related_skills: [session-analysis, skill-learner, knowledge-manager, agentic-horizon, work-queue]
scripts:
  - scripts/analysis/session-analysis.sh
  - .claude/hooks/session-signals.sh
see_also:
  - .claude/state/candidates/skill-candidates.md
  - .claude/skills/SKILLS_GRAPH.yaml
  - .claude/state/curation-log.yaml
  - .claude/state/skills-research-log.jsonl
  - .claude/state/skills-graph-review-log.jsonl
  - .claude/work-queue/working/WRK-231.md
requires: []
---

# Skills Curation Skill

> Keeps the skills library alive, well-targeted, and high-signal. Runs on a dynamic cadence that self-adjusts based on yield. Feeds from three sources: session analysis candidates, knowledge graph review, and online research.

## Quick Start

```bash
# Manual trigger
/skills-curation

# Force a run regardless of cadence schedule
/skills-curation --force

# Run only graph review (no web search)
/skills-curation --graph-only

# Run only health check
/skills-curation --health-check
```

## When This Runs

- **Trigger**: scheduled (weekly by default; cadence auto-adjusts)
- **Auto-execute**: yes — runs autonomously; surfaces created skills and spun-off WRK items for user review
- **Also**: can be invoked manually at any time

## Architecture

Three input pipelines feed a shared output stage:

```
INPUT SOURCES
├── (A) Session candidates    .claude/state/candidates/skill-candidates.md
│       ↓ new candidate signals from previous sessions
├── (B) Knowledge graph       .claude/skills/SKILLS_GRAPH.yaml
│       ↓ skill scores vs active WRK demand
└── (C) Online research       WebSearch
        ↓ new tools, deprecations, patterns in active domains

GAP TRIAGE
├── Shallow gap → auto-create skill stub in .claude/skills/
└── Deep gap    → spin off WRK item (blocked_by:[], plan_approved:false)

OUTPUT LOGGING
├── .claude/state/curation-log.yaml          (run history + cadence)
├── .claude/state/skills-research-log.jsonl  (per-run research results)
└── .claude/state/skills-graph-review-log.jsonl (graph analysis outputs)
```

---

## Phase 1 — Session Candidate Intake

**Purpose**: consume accumulated skill signals from the session analysis pipeline before running graph/research phases.

**Steps:**

1. Read `.claude/state/candidates/skill-candidates.md`
2. For each candidate listed:
   a. Check if a skill already exists at the expected path
   b. If it exists and is current → skip
   c. If it does not exist → classify as shallow or deep gap (see Gap Triage)
   d. If it exists but is stale → flag for online research in Phase 3
3. Clear processed entries from the candidates file (or mark as `processed`)

**Candidate file format expected:**

```markdown
## Candidates

- **<skill-name>** — <one-line description> | confidence: <low|medium|high> | source: <session-date>
```

---

## Phase 2 — Knowledge Graph Review

**Purpose**: identify which skill domains are load-bearing for current work and which are data-thin.

**Steps:**

1. Load `SKILLS_GRAPH.yaml`
2. Load all active WRK items from `.claude/work-queue/pending/` and `.claude/work-queue/working/`
3. For each skill node in the graph, compute a demand score:

```
demand_score = (wrk_references × 3) + (edge_count × 1) + (commit_activity × 2)
depth_score  = content_length_bucket + connected_skill_count
gap_score    = demand_score - depth_score   # positive = high demand, low data
```

4. Sort skills by gap_score descending; top 5 become research targets for Phase 3
5. Flag skills with `demand_score == 0` as archival candidates (no connection to current work)
6. Flag domains with `demand_score > threshold` but **no existing skill** as new skill candidates

**Output:**

```yaml
# Written to .claude/state/skills-graph-review-log.jsonl (one line per run)
{
  "ts": "...",
  "run_id": "...",
  "high_gap_skills": [...],
  "archival_candidates": [...],
  "new_skill_candidates": [...],
  "research_targets": [...]
}
```

---

## Phase 3 — Online Research

**Purpose**: search the web for developments relevant to the research targets surfaced in Phase 2, and identify new skills where capability gaps exist.

**Research targets come from:**

- Top N high-gap skills from graph review
- Stale skills flagged in Phase 1
- Active domain areas with no existing coverage

**For each research target:**

1. Run `WebSearch` with a focused query:
   - `"<skill domain> best practices 2026 python"`
   - `"<tool name> new features changelog 2026"`
   - `"alternatives to <tool> 2026"`
2. Assess findings:
   - New tool/pattern with no existing skill → shallow or deep gap?
   - Existing skill content outdated → queue enhancement
   - Deprecation found → flag in skill frontmatter
3. Collect research yield (findings per query)

**Yield tracking:**

```
findings_this_run = new_skills_identified + updates_queued + deprecations_found
```

---

## Phase 4 — Gap Triage

**Purpose**: classify each identified gap and route to the correct action.

### Shallow Gap

**Definition**: the pattern is known, implementation is straightforward, no domain expertise required, no architectural decisions needed.

**Examples:**
- A utility skill covering a well-documented library or CLI tool
- A workflow pattern that appeared in multiple sessions
- A candidate with high confidence in the session candidates file

**Action**: auto-create skill stub immediately (see Skill Stub Creation below).

### Deep Gap

**Definition**: requires domain expertise, significant research, architectural decisions, or user collaboration to fill properly.

**Examples:**
- A new engineering domain (e.g., subsea flow assurance) with no existing skills
- A multi-tool workflow requiring design choices
- A candidate with low confidence or unclear scope

**Action**: spin off a WRK item:

```yaml
id: WRK-NNN
title: "[domain] skill gap — needs user input"
status: pending
priority: medium
complexity: medium
blocked_by: []
plan_approved: false
plan_reviewed: false
```

WRK body must include:
- Gap description (what capability is missing)
- Demand evidence (WRK refs, commit frequency, session signals)
- Suggested approach (what research or design is needed)
- For User Review section

---

## Skill Stub Creation (Shallow Gaps)

For each shallow gap, create a minimal SKILL.md at the correct path:

**Path convention**: `.claude/skills/<category>/<subcategory>/<skill-name>/SKILL.md`

**Stub frontmatter:**

```yaml
---
name: <skill-name>
description: <one-line description from gap signal>
version: 0.1.0
category: <inferred category>
type: skill
trigger: manual
auto_execute: false
stub: true  # marks as incomplete — fill in on first use
created_by: skills-curation
created_at: <ISO timestamp>
source: <session-candidate|graph-review|online-research>
capabilities: []
tools: []
related_skills: []
requires: []
see_also: []
---

# <Skill Name>

> Stub created by skills-curation — expand on first use.

## What This Skill Does

<one-line description>

## Status

This is a stub. The following sections need to be filled in:

- [ ] Core operations / steps
- [ ] Usage examples
- [ ] Tool integrations
- [ ] Prerequisites
- [ ] Error handling

## Source Signal

Created from: <source>
Gap type: shallow
Demand evidence: <wrk refs or session date>
```

After creating the stub:

1. Update `skill-registry.yaml` if it exists
2. Update the category `INDEX.md` if it exists

---

## Phase 5 — Session-Input Health Check

**Purpose**: verify that sessions are actually producing skill signals and that the pipeline is live.

**Checks:**

| Check | Pass condition | Failure action |
|-------|---------------|----------------|
| skill-learner hook fired | At least once in last 7 days (check `.claude/state/session-signals/`) | Warn: "skill-learner hook has gone quiet" |
| candidates populated | `skill-candidates.md` has at least one entry since last curation run | Warn: "no skill candidates in N days" |
| skills committed recently | At least one skill file changed in last 7 days (git log) | Warn: "no skill updates committed in N days" |
| session-signals directory non-empty | Files exist in `.claude/state/session-signals/` | Warn: "session signals not being captured" |

**Health check output:**

```
Skills pipeline health: OK | DEGRADED | SILENT

[OK]    skill-learner hook: last fired 2026-02-19
[OK]    skill candidates: 3 entries since last run
[WARN]  recent skill commits: none in 7 days
[OK]    session signals: 12 files captured
```

If any check fails → append a `health_warning` entry to `curation-log.yaml`.

---

## Phase 6 — Yield Tracking and Cadence Adjustment

After each run, record yield and adjust cadence:

**Yield metrics:**

```yaml
yield:
  skills_created: <N>      # new skill stubs created this run
  skills_updated: <N>      # existing skills enhanced
  wrk_items_created: <N>   # deep gap WRK items spun off
  research_findings: <N>   # total research results processed
  gaps_closed: <N>         # skills_created + stubs filled
```

**Cadence adjustment logic:**

```
YIELD_THRESHOLD_HIGH = 5   # findings per run
YIELD_THRESHOLD_LOW  = 1

consecutive_low_runs counter:
  if yield < YIELD_THRESHOLD_LOW for 3 consecutive runs:
    step down cadence:  weekly → biweekly → monthly
  if yield >= YIELD_THRESHOLD_HIGH:
    step up cadence:    monthly → biweekly → weekly
    reset consecutive_low_runs = 0
```

Cadence is written back to `curation-log.yaml` after each run.

---

## Curation Log Format

State is persisted at `.claude/state/curation-log.yaml`:

```yaml
version: "1.0"
last_run: "2026-02-20T10:00:00Z"
cadence: weekly   # current active cadence
consecutive_low_runs: 0
runs:
  - run_id: "2026-02-20-001"
    ts: "2026-02-20T10:00:00Z"
    phases_run: [candidates, graph_review, online_research, gap_triage, health_check]
    yield:
      skills_created: 2
      skills_updated: 1
      wrk_items_created: 0
      research_findings: 6
      gaps_closed: 2
    health_warnings: []
    cadence_after: weekly
```

Research details go to `.claude/state/skills-research-log.jsonl` (one JSONL line per run).

Graph review details go to `.claude/state/skills-graph-review-log.jsonl` (one JSONL line per run).

---

## Cron Schedule

| Time | Job | Machine |
|------|-----|---------|
| Monday 4:00 AM | `skills-curation` (full run) | `ace-linux-1` |
| After `session-analysis.sh` | candidate intake only (Phase 1) | `ace-linux-1` |

The Monday run fires after `session-analysis.sh` (3AM) and `claude-reflect` (5AM) to have fresh candidate data available.

---

## Execution Checklist

**Pre-run:**
- [ ] `SKILLS_GRAPH.yaml` is readable
- [ ] `.claude/state/candidates/skill-candidates.md` is accessible
- [ ] Active WRK item directories are accessible
- [ ] `curation-log.yaml` is readable (or create stub if missing)

**Phase 1 — Candidates:**
- [ ] Read and parse `skill-candidates.md`
- [ ] Classify each candidate (shallow/deep/already exists)
- [ ] Mark processed entries

**Phase 2 — Graph review:**
- [ ] Load graph and compute demand/depth/gap scores
- [ ] Identify research targets (top 5 by gap score)
- [ ] Identify archival candidates (demand == 0)
- [ ] Log to `skills-graph-review-log.jsonl`

**Phase 3 — Online research:**
- [ ] Run WebSearch for each research target
- [ ] Assess findings (new/update/deprecation)
- [ ] Classify findings as shallow or deep gaps

**Phase 4 — Gap triage:**
- [ ] Auto-create stubs for shallow gaps
- [ ] Spin off WRK items for deep gaps
- [ ] Update category INDEX.md files as needed

**Phase 5 — Health check:**
- [ ] Check all four pipeline health indicators
- [ ] Emit warning summary
- [ ] Append any warnings to `curation-log.yaml`

**Phase 6 — Yield + cadence:**
- [ ] Count yield metrics
- [ ] Evaluate cadence adjustment
- [ ] Write updated `curation-log.yaml`
- [ ] Append run summary to `skills-research-log.jsonl`

---

## Integration Points

### session-analysis

`session-analysis.sh` populates `skill-candidates.md` at 3AM. The curation skill reads this file in Phase 1. The two skills share state through the candidates file — no direct coupling.

### skill-learner

`skill-learner` fires post-commit and may also create/enhance skills. The health check in Phase 5 verifies skill-learner is active. The curation skill does not duplicate skill-learner's commit-analysis logic — they operate at different granularities (per-commit vs periodic batch).

### agentic-horizon

`agentic-horizon` reassesses WRK item dispositions weekly. The curation skill reads WRK items to compute graph demand scores but does not modify them. Deep gap WRK items created by the curation skill will be picked up by agentic-horizon on its next run.

### work-queue

WRK items spun off for deep gaps follow the standard work-queue format. The curation skill assigns `blocked_by: []` and `plan_approved: false` to ensure they surface for user review before execution.

---

## Error Handling

| Error | Action |
|-------|--------|
| `SKILLS_GRAPH.yaml` unreadable | Skip Phase 2; log warning; continue with other phases |
| `skill-candidates.md` missing | Skip Phase 1; log info; continue |
| WebSearch returns no results | Log zero-yield for that target; continue |
| Skill stub creation fails (path conflict) | Log error with path; skip creation; do not overwrite |
| WRK item creation fails | Log error; record as pending manual action in curation-log.yaml |
| curation-log.yaml missing | Create it from stub template; continue |

---

## Related Skills

- [session-analysis](../session-analysis/SKILL.md) — populates skill-candidates.md
- [skill-learner](../skill-learner/SKILL.md) — post-commit skill extraction
- [knowledge-manager](../knowledge-manager/SKILL.md) — broader knowledge capture
- [agentic-horizon](../agentic-horizon/SKILL.md) — WRK item disposition management
- [work-queue](../work-queue/SKILL.md) — WRK item lifecycle

---

## Version History

- **1.0.0** (2026-02-20): Initial release — three-pipeline curation (session candidates, graph review, online research), gap triage (shallow auto-create / deep WRK spin-off), session-input health check, yield tracking, dynamic cadence adjustment.
