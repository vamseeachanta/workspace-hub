# Terminal 2 — Hermes: Dead Skill Audit + Correction Hotspots + Memory Dedup

## Context
We are in /mnt/local-analysis/workspace-hub on ace-linux-1.
This is an analysis-only session for GH issue #1720.
Use `uv run` for all Python. Do NOT ask the user any questions.
Do NOT modify any skills, scripts, or source code.
Commit to main and push after each major deliverable.
`git pull origin main --rebase` before every push.

## YOUR WRITE TERRITORY
- `analysis/cross-agent-audit-20260402/phase-c-dead-skills.md`
- `analysis/cross-agent-audit-20260402/phase-d-correction-hotspots.md`
- `analysis/cross-agent-audit-20260402/phase-f-memory-dedup.md`
- `analysis/cross-agent-audit-20260402/phase-c-data/`
- `analysis/cross-agent-audit-20260402/phase-d-data/`
- `analysis/cross-agent-audit-20260402/phase-f-data/`

## DO NOT WRITE TO
- `analysis/cross-agent-audit-20260402/phase-a-*` (Terminal 1)
- `analysis/cross-agent-audit-20260402/phase-b-*` (Terminal 1)
- `analysis/cross-agent-audit-20260402/phase-e-*` (Terminal 3)
- `analysis/cross-agent-audit-20260402/phase-g-*` (Terminal 3)
- Any file outside `analysis/`

---

## TASK 1: Phase C — Dead Skill Audit

### Data sources
1. `skill-scores.yaml`: `.claude/state/skill-scores.yaml` — 547 skills with `tier` field (active/dormant/dead)
2. Full skill inventory across 5 repos (691 active skills total, after excluding `_archive/`, `_internal/`, `_runtime/`, `_core/`, `session-logs/`):
   - `.claude/skills/` — 387 (workspace-hub root)
   - `CAD-DEVELOPMENTS/.claude/skills/` — 182
   - `worldenergydata/.claude/skills/` — 20
   - `achantas-data/.claude/skills/` — 13
   - `assetutilities/.claude/skills/` — 3
3. Git log: `git log --since=2026-01-01 --name-only --pretty=format:""` to find recently modified files
4. Hermes local skills: `~/.hermes/skills/` — 86 skills (names may overlap with workspace-hub)

### Analysis to produce

1. **Tier distribution**: Count skills by tier from skill-scores.yaml. How many active/dormant/dead?

2. **Unscored skills**: 691 total active skills vs 547 scored — which 144 skills have no score at all? (These are from repos not covered by skill-scores.yaml, or newly created.)

3. **Dead skill classification**: For each skill with `tier: dead`:
   - Check if the skill's domain directory has files modified in the last 90 days (via git log)
   - If domain is active but skill is dead: **dormant-but-needed** (wrong triggers? bad name?)
   - If domain is also inactive: **truly-dead** (candidate for archive)
   - If skill name doesn't match any directory/module: **orphaned** (stale reference)

4. **Cross-repo skill overlap**: Check for skills with same name across different repos. Identify duplicates that should be consolidated.

5. **Hermes vs workspace-hub overlap**: 5 known name collisions (code-review, dspy, obsidian, systematic-debugging, writing-plans). Are the contents divergent or duplicated?

### Output
Write `analysis/cross-agent-audit-20260402/phase-c-dead-skills.md`:
- Tier distribution table
- Unscored skills list
- Dead skill classifications (truly-dead / dormant-but-needed / orphaned) with counts
- Cross-repo overlap table
- Hermes collision analysis
- Recommendations: archive candidates, trigger fixes, consolidation candidates

### Commit
```
chore(analysis): Phase C — dead skill audit across 691 skills (#1720)
```

---

## TASK 2: Phase D — Correction Hotspot Analysis

### Data sources
1. `.claude/state/corrections/*.jsonl` — 68 files, 8,965 total corrections
   Format per line: `{"type":"correction","tool":"Edit","file":"...","description":"...","timestamp":"..."}`
2. Claude orchestrator logs (for file-edit frequency context): `logs/orchestrator/claude/session_*.jsonl`
3. Hermes orchestrator: `logs/orchestrator/hermes/session_*.jsonl`

### Analysis to produce

1. **Top 20 correction hotspot files**: Files appearing most frequently in corrections. Include count, percentage of total.

2. **Top 10 correction hotspot directories/modules**: Group files by parent module.

3. **Correction patterns**: Parse `description` fields (or `cmd`/`file` context) to identify recurring correction types:
   - Import errors / missing dependencies
   - YAML/JSON parse errors
   - Test failures
   - Path errors (file not found)
   - Git workflow issues
   - Type errors

4. **Test coverage gap signal**: For each hotspot file, check if a corresponding test file exists:
   - `src/pkg/module.py` → `tests/pkg/test_module.py`
   - If no test: flag as test coverage gap

5. **Cross-agent correction overlap**: Are the same files corrected by both Claude and Hermes?

6. **Temporal trends**: Corrections per week — increasing, decreasing, or stable?

### Output
Write `analysis/cross-agent-audit-20260402/phase-d-correction-hotspots.md`:
- Top 20 file hotspots table
- Top 10 module hotspots table
- Correction pattern taxonomy with counts
- Test coverage gap flags
- Temporal trend chart (text-based)
- Recommendations: prioritized list of files needing test coverage or refactoring

### Commit
```
chore(analysis): Phase D — correction hotspot analysis from 8,965 corrections (#1720)
```

---

## TASK 3: Phase F — Memory Deduplication

### Data sources
1. Hermes MEMORY.md: `~/.hermes/memories/MEMORY.md` — 14 lines, §-separated entries
   Contents: environment facts, project knowledge, tool quirks
2. Hermes USER.md: `~/.hermes/memories/USER.md` — 10 lines, §-separated entries
   Contents: user preferences, identity, work patterns
3. Claude memory: `~/.claude/projects/-mnt-local-analysis-workspace-hub/` (if exists)
4. Claude state: `.claude/state/cc-user-insights.yaml` (if exists)
5. Claude state: `.claude/state/learned-patterns.json` (if exists)
6. Codex rules: `~/.codex/rules/default.rules`
7. Codex config: `~/.codex/config.toml`
8. AGENTS.md files across 24 repos: `find /mnt/local-analysis/workspace-hub -maxdepth 2 -name AGENTS.md`
9. CLAUDE.md files across 24 repos: `find /mnt/local-analysis/workspace-hub -maxdepth 2 -name CLAUDE.md`

### Analysis to produce

1. **Hermes memory inventory**: Parse §-separated entries, categorize each as:
   - environment_fact, user_preference, convention, project_knowledge, tool_quirk

2. **Claude memory inventory**: Parse whatever format exists in Claude's memory stores.

3. **Codex knowledge inventory**: Parse rules file and config for embedded knowledge.

4. **Cross-agent fact overlap**: Identify facts stated in ≥2 agent stores. For each overlap:
   - Are they consistent? (same fact, same values)
   - Are they contradictory? (flag for resolution)
   - Should they be promoted to shared config (AGENTS.md, harness-config.yaml)?

5. **AGENTS.md/CLAUDE.md audit**: For each of 24 repos:
   - Is AGENTS.md a pointer to workspace-hub canonical, or standalone?
   - Does CLAUDE.md content match actual repo structure?
   - Are there stale references?

6. **Promotion candidates**: Facts that should move from agent-private memory to shared ecosystem:
   - `uv run` convention → already in AGENTS.md? (check)
   - Workspace-hub path → in harness-config.yaml? (check)
   - User preferences → in a shared user profile? (propose)

### Output
Write `analysis/cross-agent-audit-20260402/phase-f-memory-dedup.md`:
- Per-agent memory inventory tables
- Cross-agent overlap matrix
- Contradiction flags
- AGENTS.md/CLAUDE.md freshness table (24 repos)
- Promotion candidate list with proposed destination

### Commit
```
chore(analysis): Phase F — memory dedup + AGENTS.md audit across 24 repos (#1720)
```

---

Post a brief progress comment on GH issue #1720 when done:
```
Terminal 2 (Hermes) complete:
- Phase C: dead skill audit at analysis/cross-agent-audit-20260402/phase-c-dead-skills.md
  - [N] truly-dead, [N] dormant-but-needed, [N] orphaned
- Phase D: correction hotspots at analysis/cross-agent-audit-20260402/phase-d-correction-hotspots.md
  - Top hotspot: [file] ([N] corrections)
- Phase F: memory dedup at analysis/cross-agent-audit-20260402/phase-f-memory-dedup.md
  - [N] cross-agent overlaps, [N] promotion candidates
```
