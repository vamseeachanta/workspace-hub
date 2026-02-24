---
name: skills-researcher
description: Periodic skills curation agent — research online developments, review knowledge graph against WRK demand, identify gaps, create/update skills, and log yield for dynamic cadence adjustment
version: 1.0.0
category: workspace-hub
type: skill
trigger: scheduled
cadence: dynamic  # starts daily; steps down to weekly then monthly based on yield
auto_execute: true
capabilities:
  - online_research
  - knowledge_graph_review
  - skill_gap_detection
  - skill_creation
  - skill_update
  - wrk_gap_surfacing
  - cadence_adjustment
  - yield_logging
tools: [Read, Write, Edit, Bash, Grep, Glob, Task]
related_skills: [claude-reflect, agentic-horizon, knowledge-manager, work-queue]
scripts:
  - scripts/skills/review-skills-graph.sh
  - scripts/skills/check-skill-pipeline-health.sh
state_files:
  - .claude/state/skills-research-log.jsonl
  - .claude/state/skills-graph-review-log.jsonl
  - .claude/state/curation-log.yaml
see_also:
  - .claude/work-queue/working/WRK-229.md
  - .claude/skills/coordination/workspace/claude-reflect/SKILL.md
---

# Skills Researcher

> Periodic agent that researches online developments, reviews the skills knowledge
> graph against active WRK demand, identifies gaps, curates or creates skills, and
> self-adjusts its cadence based on yield.

## When This Runs

- **Trigger**: dynamic cadence — starts daily, auto-adjusts to weekly or monthly
- **Auto-execute**: fully autonomous; surfaces deep gaps and new WRK items for user review
- **Manual**: invoke `/skills-researcher` at any time to run immediately

## Cadence Adjustment Logic

```
YIELD_THRESHOLD = 3  # findings per run (updates + new skills)

consecutive_low = 0
for each run:
  if yield >= YIELD_THRESHOLD:
    consecutive_low = 0
    if cadence != "daily": step UP cadence
  else:
    consecutive_low += 1
    if consecutive_low >= 3:
      step DOWN cadence (daily → weekly → monthly)
      consecutive_low = 0
```

Cadence state is persisted in `.claude/state/curation-log.yaml`.

## What It Does

### Phase 1 — Knowledge Graph Review

1. Run `scripts/skills/review-skills-graph.sh` (or invoke inline)
2. Load `SKILLS_GRAPH.yaml` (if present) or scan `.claude/skills/` directory tree
3. Load active WRK items from `.claude/work-queue/pending/`, `working/`, `blocked/`
4. Score each skill domain by:
   - (a) frequency referenced in active WRK item text
   - (b) recency of git commits touching that domain
   - (c) skill depth (content length, connection count, last_updated)
5. Produce three lists:
   - **Priority list**: high demand, low data → research targets this run
   - **Archival candidates**: zero WRK connections in 60+ days
   - **Gap candidates**: high-demand domain with no skill → creation targets

### Phase 2 — Gap Triage

For each gap candidate apply the triage rule:

| Gap type | Criteria | Action |
|----------|----------|--------|
| Shallow gap | Known domain, missing coverage | Agent creates skill autonomously this run |
| Deep gap | Requires domain expertise or significant research | Spin off `WRK-NNN: [domain] skill gap` for user |

Deep-gap WRK items include: the domain, demand evidence (WRK refs + commit count),
why it matters, and a suggested approach.

### Phase 3 — Online Research

For each skill in the Priority list (top N by score):

1. Identify the tool/framework/pattern the skill covers
2. Research recent developments (use WebSearch or WebFetch if available; otherwise
   scan local state files for recent patterns)
3. For each finding: update the relevant SKILL.md, or create a new skill if the
   finding covers a capability gap
4. Count findings (updates + new skills created) → this run's yield

### Phase 4 — Index + Registry Update

After curation:
1. Update `INDEX.md` files in affected skill directories
2. Update `.claude/state/skill-registry.yaml` with new skill entries
3. Update skill `version` and `last_updated` fields where content changed

### Phase 5 — Yield Logging

Append one JSON object to `.claude/state/skills-research-log.jsonl`:

```json
{
  "run_id": "skills-research-2026-02-24T05:00:00Z",
  "date": "2026-02-24",
  "cadence_before": "daily",
  "cadence_after": "daily",
  "consecutive_low_runs": 0,
  "skills_updated": 3,
  "skills_created": 1,
  "wrk_items_created": 0,
  "archival_candidates": ["skill-a", "skill-b"],
  "yield": 4,
  "priority_targets": ["orcaflex-specialist", "qgis"],
  "duration_seconds": 42
}
```

Update `curation-log.yaml` with `last_run` and `cadence`.

## Execution Pattern

```
1.  Run review-skills-graph.sh → priority_list, archival_candidates, gap_candidates
2.  For each deep gap → create WRK item (present to user before writing)
3.  For each shallow gap → create skill autonomously
4.  For each skill in priority_list (top 10) → research + update or create
5.  Update INDEX.md and skill-registry.yaml
6.  Append yield log entry → skills-research-log.jsonl
7.  Adjust cadence in curation-log.yaml
8.  Run check-skill-pipeline-health.sh → append health flag to log entry
```

## Output Locations

```
.claude/state/
  skills-research-log.jsonl       # one entry per run (yield + cadence)
  skills-graph-review-log.jsonl   # one entry per graph review pass
  curation-log.yaml               # cadence state + last_run

.claude/skills/<domain>/<skill>/
  SKILL.md                        # updated or newly created skills

.claude/work-queue/pending/
  WRK-NNN.md                      # deep-gap items (created after user review)
```

## User Interaction

- Agent runs phases 1–5 autonomously
- For deep-gap WRK item creation: presents proposed item to user before writing file
- Presents a brief run summary after each execution
- No user interaction needed for shallow gaps or skill updates

---

## Version History

- **1.0.0** (2026-02-24): Initial release — implements WRK-229 online research pipeline
