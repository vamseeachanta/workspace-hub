# /improve Skill — Autonomous Ecosystem Improvement

## Context

The workspace-hub has `/insights` (read-only reports) and `/reflect` (auto-generates skills from git patterns), but neither touches core config files or existing skills. Sessions accumulate learnings — corrections, patterns, debugging lessons — that decay because nobody manually updates CLAUDE.md, rules, memory, or skills. This skill closes the loop: it reads session signals and autonomously improves the entire ecosystem at session exit.

## Design Summary

- **Skill name**: `improve`
- **Command**: `/improve`
- **Trigger**: Session-exit (instruction in CLAUDE.md) + manual `/improve`
- **Mode**: Fully autonomous — apply changes directly, log what changed
- **Scope**: CLAUDE.md, `.claude/rules/*.md`, `.claude/memory/`, `.claude/skills/**/*.md`, `.claude/docs/`

## Cross-Machine / Multi-User Behavior

**Everything syncs via git. No user-local memory.**

| Target | Syncs via git? | Notes |
|---|---|---|
| Skill + command files | Yes | All users get the skill |
| CLAUDE.md, rules, docs | Yes | Shared improvements |
| `.claude/memory/` (repo) | Yes | Shared institutional knowledge |
| `.claude/skills/**/*.md` | Yes | Skill improvements shared |
| `.claude/state/` (changelog) | No (gitignored) | Per-machine audit trail |

### Repo-Only Memory (No User-Local)

All memory lives in the repo at `.claude/memory/`:
- `KNOWLEDGE.md` — main institutional knowledge file
- Topic files: `orcawave-lessons.md`, `aqwa-lessons.md`, etc.
- Machine-specific paths use environment variables or placeholders, not hardcoded paths

Work happens across multiple workstations — everything must be in the repo.

### One-Time Migration Task

Merge & deduplicate existing user-local memory into repo memory:
- Source: `C:\Users\ansystech\.claude\projects\D--workspace-hub\memory\MEMORY.md` + topic files
- Target: `.claude/memory/KNOWLEDGE.md` + topic files
- Convert machine-specific paths to env var placeholders (e.g., `$AQWA_HOME/bin/...`)
- Deduplicate entries already captured elsewhere (rules, docs)

## Files to Create

### 1. Skill Definition
**Path**: `.claude/skills/workspace-hub/improve/SKILL.md`

```yaml
---
name: improve
description: Autonomous session-exit skill that improves all ecosystem files from session learnings
version: 1.0.0
category: workspace-hub
type: skill
trigger: session-exit
tools: [Read, Write, Edit, Bash, Grep, Glob, Task]
related_skills: [claude-reflect, insights]
capabilities: [config_improvement, skill_lifecycle, memory_management, rule_enhancement, doc_updates]
---
```

### 2. Command Registration
**Path**: `.claude/commands/workspace-hub/improve.md`

```yaml
---
name: improve
aliases: [self-improve, ecosystem-improve]
description: Improve ecosystem files (config, skills, memory, rules, docs) from session learnings
category: workspace-hub
---
```

### 3. Repo Memory (initial from migration)
**Path**: `.claude/memory/KNOWLEDGE.md`

Merged & deduplicated from user-local memory. Sections:
- Environment Conventions (env vars, not hardcoded paths)
- Tool/Solver Knowledge (OrcaWave, AQWA, BEMRosetta)
- Debugging Protocol
- Cross-Platform Requirements
- Key Patterns

**Path**: `.claude/memory/orcawave-lessons.md` — migrated topic file
**Path**: `.claude/memory/aqwa-lessons.md` — migrated topic file

### 4. Changelog State File
**Path**: `.claude/state/improve-changelog.yaml`

```yaml
runs:
  - date: ISO-timestamp
    session_id: xxx
    changes:
      - file: .claude/skills/data/polars/SKILL.md
        action: "enhanced with correction pattern"
        diff_summary: "+3 lines in Quick Reference"
      - file: .claude/memory/KNOWLEDGE.md
        action: "added AQWA mesh lesson"
        diff_summary: "+2 lines in Tool/Solver Knowledge"
    skills_lifecycle:
      created: 0
      enhanced: 1
      deprecated: 0
      archived: 0
```

## Files to Modify

### 5. CLAUDE.md — Two Modifications
**Path**: `D:\workspace-hub\CLAUDE.md`

**A) Add to Core Rules:**
```
7. **Session-exit improvement** - Run `/improve` before ending every session
```

**B) Update Retrieval-Led Reasoning:**
```
Consult `.claude/docs/`, `.claude/rules/`, `.claude/memory/`, and project `CLAUDE.md` before relying on general knowledge.
```

## Core Workflow (inside SKILL.md)

### Phase 1: COLLECT — Gather Session Signals

Data sources:
1. `.claude/state/pending-reviews/memory-updates.jsonl` — memory candidates
2. `.claude/state/pending-reviews/insights.jsonl` — insight candidates
3. `.claude/state/pending-reviews/errors.jsonl` — error patterns
4. `.claude/state/pending-reviews/skill-candidates.jsonl` — skill gaps
5. `.claude/state/corrections/.recent_edits` — correction patterns
6. `.claude/state/accumulator.json` — aggregated metrics
7. `.claude/state/patterns/` — patterns from `/reflect`
8. Current session context — what was learned in THIS session

### Phase 2: CLASSIFY — Route Improvements to Targets

| Signal Type | Target | Example |
|---|---|---|
| Institutional knowledge | `.claude/memory/KNOWLEDGE.md` | "OrcaWave .frequencies returns Hz" |
| Domain-specific lesson | `.claude/memory/<topic>.md` | "AQWA needs QPPL DIFF for diffraction" |
| Repeated correction | `.claude/rules/*.md` | "Always validate freq order" |
| Skill gap / new capability | `.claude/skills/**/ (create)` | "No skill for PDF table extraction" |
| Skill correction | `.claude/skills/**/ (enhance)` | "Polars skill missing lazy frame pattern" |
| Underperforming skill | `.claude/skills/**/ (deprecate)` | "Skill never used in 90 days, superseded" |
| Cross-session pattern | `CLAUDE.md` Core Rules | "Batch operations reduce errors" |
| Resource drift | `CLAUDE.md` Resource Index | "New agent in agents/devops/" |
| Documentation gap | `.claude/docs/` | "Orchestrator pattern needs update" |

### Phase 3: GUARD — Safety Checks Before Writing

1. **Size guards**:
   - CLAUDE.md: 4KB budget
   - KNOWLEDGE.md: 200-line limit
   - Rules files: 400-line max per file
   - SKILL.md files: 400-line max

2. **Dedup check**: Read target file, verify improvement doesn't already exist

3. **No-clobber rule**: If target file has uncommitted changes, skip it

4. **Skill lifecycle gates**:
   - **Create**: Only when no existing skill covers the capability (search first)
   - **Deprecate**: Only when unused for 90+ days AND superseded by another skill
   - **Archive**: Move deprecated skills to `.claude/skills/_archive/` (never delete)

### Phase 4: APPLY — Write Improvements

**CLAUDE.md**:
- Resource Index: Scan actual directories, update counts/references
- Core Rules: Add patterns confirmed across 3+ sessions
- Strategy: Edit tool for surgical section updates

**Rules files** (`.claude/rules/*.md`):
- Add examples from real corrections
- Add new subsections when a correction category repeats 3+ times
- Cross-reference related rules
- Strategy: Append to existing sections, never restructure

**Repo memory** (`.claude/memory/`):
- Add debugging lessons, tool conventions, API quirks
- Use env var placeholders for paths (never hardcode machine paths)
- Prune entries confirmed outdated
- Create new topic file if section exceeds 10 entries

**Skills** (`.claude/skills/**/*.md`) — FULL LIFECYCLE:
- **Enhance**: Add examples, fix instructions, improve prompts from corrections
- **Create**: New SKILL.md when repeated pattern has no matching skill (follow existing template)
- **Deprecate**: Add deprecation notice to SKILL.md frontmatter when unused 90+ days
- **Archive**: Move deprecated skills to `_archive/` with reason and date
- **Reorganize**: Move miscategorized skills to correct category directory
- Strategy: Read existing skill, understand its structure, make minimal targeted edits

**Docs** (`.claude/docs/`):
- Update stale references
- Add missing documentation for new patterns
- Strategy: Edit existing files, create new only for clear gaps

### Phase 5: LOG — Record Changes

Write to `.claude/state/improve-changelog.yaml`:
- Timestamp, changes list with file/action/diff_summary
- Skills lifecycle metrics: created/enhanced/deprecated/archived counts
- signals_processed, changes_applied, signals_skipped (with reason)

### Phase 6: CLEANUP — Mark Signals Consumed

Move processed signals from `pending-reviews/*.jsonl` to archive so they aren't reprocessed.

## Decision Logic (Scoring)

| Factor | Weight | Criteria |
|---|---|---|
| Recurrence | 40% | Same pattern N times (1x=0.2, 2x=0.5, 3+=0.8) |
| Severity | 30% | Blocked work (1.0), warning (0.5), info (0.2) |
| Freshness | 15% | This session (1.0), last 7 days (0.7), older (0.3) |
| Specificity | 15% | Actionable (1.0), vague (0.3) |

**Thresholds**:
- Score >= 0.6: Apply immediately
- Score 0.3–0.59: Stage for accumulation (may trigger next session)
- Score < 0.3: Discard

**Exceptions** (bypass scoring):
- Direct user statements ("remember this", "always do X") → apply immediately
- Skill deprecation → requires 90-day inactivity evidence regardless of score

## Skill Lifecycle Details

### Creating New Skills
```
1. Search .claude/skills/**/*.md for existing coverage
2. If no match, create at .claude/skills/<category>/<subcategory>/<name>/SKILL.md
3. Follow existing SKILL.md template (YAML frontmatter + markdown sections)
4. Mark as auto_generated: true in frontmatter
5. Log in changelog with source pattern evidence
```

### Enhancing Existing Skills
```
1. Read current SKILL.md
2. Identify section to update (Quick Reference, examples, error handling)
3. Apply surgical edit (append examples, fix instructions)
4. Bump patch version in frontmatter
5. Log enhancement in changelog
```

### Deprecating Skills
```
1. Verify: no usage in last 90 days (check session logs, git history)
2. Verify: superseded by another skill (identify replacement)
3. Add to frontmatter: deprecated: true, deprecated_date, replacement_skill
4. Do NOT delete — archive in next pass
```

### Archiving Skills
```
1. Move from .claude/skills/<category>/ to .claude/skills/_archive/<category>/
2. Add archive metadata: archive_date, reason, original_path
3. Update any cross-references in other skills
```

## Integration with Existing Skills

- **Consumes** `/reflect` output: patterns from `.claude/state/patterns/`
- **Consumes** `/insights` output: session reports
- **Complements** session hooks: `session-review.sh` produces JSONL signals
- **Subsumes** `/reflect`'s skill creation: `/improve` handles all skill lifecycle now
- **Does NOT duplicate**: `/reflect` analyzes git history, `/improve` acts on signals

## Verification Plan

1. **Migration**: Run one-time merge of user-local memory into `.claude/memory/`
2. **Dry run**: Invoke `/improve` manually, verify it reads signals and classifies correctly
3. **Check changelog**: Verify `.claude/state/improve-changelog.yaml` records changes
4. **Check targets**: Read modified files to confirm improvements are valid
5. **Size check**: CLAUDE.md under 4KB, KNOWLEDGE.md under 200 lines
6. **Dedup test**: Run `/improve` twice — second run should find nothing new
7. **Skill lifecycle**: Verify create/enhance/deprecate/archive all work
8. **Cross-machine**: Pull repo on another machine, verify skill loads and memory is available
