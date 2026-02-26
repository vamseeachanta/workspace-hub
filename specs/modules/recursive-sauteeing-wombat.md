# Plan: WRK-299 + WRK-300

## Context

Sessions currently have fragmented learning overhead: 4 separate skills (/insights, /reflect,
/knowledge, /improve), candidate files that accumulate unread, and post-task hooks that
interrupt work flow. Two work items fix this:

- **WRK-299**: Create `/comprehensive-learning` — single fire-and-forget command that runs
  the full learning pipeline, actions all candidate files, and is safe for cron scheduling.
  Strip blocking behavior from post-task hooks so sessions stay lean.
- **WRK-300**: Evolve the `workstations` skill from a static registry to an active
  multi-machine routing skill with software capability maps.

---

## WRK-299: comprehensive-learning skill

### Files to create / modify

| Action | Path |
|--------|------|
| CREATE | `.claude/skills/workspace-hub/comprehensive-learning/SKILL.md` |
| MODIFY | `.claude/hooks/post-task-review.sh` — strip blocking checklist |

### Skill: SKILL.md structure

**YAML frontmatter:**
```yaml
---
name: comprehensive-learning
description: >
  Single fire-and-forget command that runs the full session learning pipeline:
  insights → reflect → knowledge → improve → action-candidates → report.
  Machine-aware. Safe for cron scheduling. Replaces running 4 skills manually.
version: 1.0.0
category: workspace-hub
author: workspace-hub
type: skill
invoke: comprehensive-learning
auto_execute: false
tools: [Read, Write, Edit, Bash, Grep, Glob, Task]
related_skills: [workspace-hub/improve, workspace-hub/claude-reflect, workspace-hub/session-end]
capabilities: [session-learning, ecosystem-improvement, candidate-actioning, cron-safe]
tags: [learning, meta, session-exit, cron, multi-machine]
platforms: [all]
wrk_ref: WRK-299
---
```

**6-Phase pipeline (sequential):**

**Phase 1 — Insights**
Invoke `/insights` skill. Sources consumed:
- `.claude/state/session-signals/*.jsonl`
- `.claude/state/cc-insights/*.json`
- `.claude/state/sessions/*.json`
- `.claude/state/daily-summaries/*.md`

**Phase 2 — Reflect**
Invoke `/reflect` (claude-reflect scripts). Sources:
- `.claude/state/reflect-history/`
- `.claude/state/trends/*.json`
- `git log --all --oneline` across repos

**Phase 3 — Knowledge**
Invoke `/knowledge`. Sources: phase 1+2 output + session context.

**Phase 4 — Improve**
Invoke `/improve`. Sources:
- `.claude/state/corrections/*.jsonl`
- `.claude/state/accumulator.json`
- `.claude/state/patterns/`
- `.claude/state/pending-reviews/*.jsonl`
- `.claude/state/learned-patterns.json`
- `.claude/state/skill-scores.yaml`
- `.claude/state/cc-user-insights.yaml`

**Phase 5 — Action Candidates** (GAP FILL — not covered by existing skills)
Read each candidate file; for non-trivial, non-null entries create WRK item via
`scripts/work-queue/next-id.sh`. Clear candidate file after processing.
Candidate files:
- `.claude/state/candidates/skill-candidates.md`
- `.claude/state/candidates/script-candidates.md`
- `.claude/state/candidates/hook-candidates.md`
- `.claude/state/candidates/mcp-candidates.md`
- `.claude/state/candidates/agent-candidates.md`

WRK auto-creation pattern (reuse from consume-signals.sh):
```bash
NEXT_ID=$(bash scripts/work-queue/next-id.sh)
# Write .claude/work-queue/pending/WRK-${NEXT_ID}.md
# Update .claude/work-queue/state.yaml last_id
```

Skip Phase 5 if `$CL_MACHINE_MODE == skip-candidates` (ace-linux-2, to avoid duplicates).

**Phase 6 — Report**
Write `.claude/state/learning-reports/$(date +%Y-%m-%d-%H%M).md` with:
- One-line result per phase (DONE / SKIPPED / FAILED + reason)
- Count of WRK items created in Phase 5
- Total elapsed time

Exit 0 if all mandatory phases pass; exit 1 on fatal failure (log and continue for
non-fatal phase failures).

### Machine routing

```bash
MACHINE=$(hostname | tr '[:upper:]' '[:lower:]')
case "$MACHINE" in
  ace-linux-1)        CL_MACHINE_MODE=full ;;
  ace-linux-2)        CL_MACHINE_MODE=skip-candidates ;;
  acma-ansys05)       CL_MACHINE_MODE=lightweight ;;   # Phase 1 only
  *)                  CL_MACHINE_MODE=full ;;
esac
export CL_MACHINE_MODE
```

Lightweight mode (acma-ansys05): run Phase 1 only, write report, exit.

### Cron examples (document in SKILL.md under ## Scheduling)

```bash
# ace-linux-1: nightly 22:00
0 22 * * * cd /mnt/local-analysis/workspace-hub && claude --skill comprehensive-learning >> .claude/state/learning-reports/cron.log 2>&1

# acma-ansys05: nightly 23:00 (lightweight — Phase 1 only)
0 23 * * * cd /path/to/workspace && claude --skill comprehensive-learning >> cron.log 2>&1
```

### post-task-review.sh change

**Current**: Shows counts + multi-line checklist (interactive, interrupts flow).
**New**: Replace checklist with a single line:
```
→ Run /comprehensive-learning post-session to process learnings.
```
Keep all signal reads (counts display is fine). Remove the 4-item manual checklist block.
This is a 3-5 line edit to the existing file.

---

## WRK-300: workstations skill — multi-machine routing

### Files to modify

| Action | Path |
|--------|------|
| MODIFY | `.claude/skills/workspace-hub/workstations/SKILL.md` |

### Changes to SKILL.md

**1. Extend machine registry table** with `programs` + flags column. Add a separate
`## Software Capability Map` section (YAML block):

```yaml
machines:
  ace-linux-1:
    hostname: ace-linux-1
    programs: [python, uv, git, claude-code, worldenergydata, digitalmodel,
               assetutilities, assethold, legal-scan, pytest]
    exclusive: []
    shares_hub: null
    isolated: false
    cron_variant: full

  ace-linux-2:
    hostname: ace-linux-2
    programs: [python, uv, git, claude-code, digitalmodel, assetutilities]
    exclusive: []
    shares_hub: ace-linux-1
    isolated: false
    cron_variant: skip-candidates

  acma-ansys05:
    hostname: ACMA-ANSYS05
    programs: [orcaflex, ansys, python, office]
    exclusive: [orcaflex, ansys]
    shares_hub: null
    isolated: true
    cron_variant: lightweight

  acma-ws014:
    hostname: ACMA-WS014
    programs: [office, windows-tools]
    exclusive: []
    shares_hub: null
    isolated: false
    cron_variant: full

  gali-linux-compute-1:
    hostname: TBD
    programs: [cfd, fea, python, batch]
    exclusive: []
    shares_hub: null
    isolated: false
    cron_variant: full
```

**2. Add `## Routing Rules` section**

Routing decision (for use when setting `computer:` on a new WRK item):

| Keyword in WRK title/tags | Recommended machine |
|---------------------------|---------------------|
| orcaflex, ansys, aqwa | acma-ansys05 |
| office, windows, excel | acma-ws014 or acma-ansys05 |
| cfd, fea, heavy-compute | gali-linux-compute-1 |
| worldenergydata, hub, claude | ace-linux-1 |
| everything else | ace-linux-1 or ace-linux-2 |

**3. Add `## Multi-machine WRK Items` section**

For tasks spanning machines, allow list:
```yaml
computer: [acma-ansys05, ace-linux-1]
```
Document conventions for handoff steps.

**4. Add `## comprehensive-learning Integration` section**

Reference WRK-299: `cron_variant` field maps directly to `CL_MACHINE_MODE` in the
comprehensive-learning skill. No separate config needed.

**5. Fix duplication**: Current SKILL.md has `## WRK Item Integration` duplicated twice
(lines ~62-70 and ~145-160). Remove the second copy.

---

## Execution order

1. **WRK-300 first** (smaller, provides machine config consumed by WRK-299)
2. **WRK-299 second** (references workstations config for machine routing)

## Verification

### WRK-299
```bash
# Dry run — check skill loads
claude --skill comprehensive-learning --help

# Manual run
cd /mnt/local-analysis/workspace-hub
claude --skill comprehensive-learning

# Verify report written
ls .claude/state/learning-reports/

# Verify candidate files cleared
cat .claude/state/candidates/skill-candidates.md

# Confirm post-task-review.sh no longer shows checklist
bash .claude/hooks/post-task-review.sh
```

### WRK-300
```bash
# Verify SKILL.md loads cleanly (no YAML parse errors)
python3 -c "import yaml; yaml.safe_load(open('.claude/skills/workspace-hub/workstations/SKILL.md').read().split('---')[1])"

# Confirm duplicate section removed
grep -n "WRK Item Integration" .claude/skills/workspace-hub/workstations/SKILL.md
# Should return exactly 1 match
```
