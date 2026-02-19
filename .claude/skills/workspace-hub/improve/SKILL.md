---
name: improve
description: Autonomous session-exit skill that improves all ecosystem files from session learnings
version: 1.4.0
category: workspace-hub
author: workspace-hub
type: skill
trigger: session-exit
auto_execute: false
tools: [Read, Write, Edit, Bash, Grep, Glob, Task]
related_skills: [claude-reflect, insights, knowledge, skill-learner, skill-creator]
capabilities:
  - config_improvement
  - skill_lifecycle
  - memory_management
  - rule_enhancement
  - doc_updates
  - ecosystem_review
tags: [self-improvement, ecosystem, session-exit, meta]
platforms: [all]
---

# /improve — Autonomous Ecosystem Improvement

Reads session signals (corrections, patterns, errors, insights) and autonomously improves ecosystem files. Runs at session exit or manually via `/improve`.

## Trigger Conditions

- User invokes `/improve` manually
- Session exit (per CLAUDE.md Core Rule #7)
- After significant debugging sessions with new learnings

## Core Workflow

### Phase 1: COLLECT — Gather Session Signals

Scan these data sources for improvement candidates:

1. `.claude/state/pending-reviews/memory-updates.jsonl` — memory candidates
2. `.claude/state/pending-reviews/insights.jsonl` — insight candidates
3. `.claude/state/pending-reviews/errors.jsonl` — error patterns
4. `.claude/state/pending-reviews/skill-candidates.jsonl` — skill gaps
5. `.claude/state/corrections/.recent_edits` — correction patterns
6. `.claude/state/accumulator.json` — aggregated metrics
7. `.claude/state/patterns/` — patterns from `/reflect`
8. `.claude/state/pending-reviews/ecosystem-review.jsonl` — ecosystem health signals (from stop hook)
9. Current session context — what was learned in THIS session

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
| Ecosystem health signal | Phase 3 review queue | "Skill sprawl: 350+ active skills" |
| Memory bloat signal | Phase 3 review queue | "MEMORY.md exceeds 200 lines" |

### Phase 3: ECOSYSTEM REVIEW — Structural Health Assessment

Assess the overall health of ecosystem files and recommend reallocation. This phase is fed by signals from the `ecosystem-health-check.sh` stop hook AND by scanning the filesystem directly.

**Data sources:**
1. `.claude/state/pending-reviews/ecosystem-review.jsonl` — automated health check signals
2. Direct filesystem scan of `.claude/skills/`, `.claude/memory/`, `.claude/rules/`

**Checks performed:**

| Check | Signal | Action |
|---|---|---|
| **Stale skills** | No session usage in 90+ days (via `last_used` in frontmatter) | Flag for deprecation review |
| **Index quality** | Skills missing `capabilities:`, `tags:`, or `related:` frontmatter | Flag for metadata enrichment |
| **Skill overlap** | 2+ skills with >70% description similarity | Flag for consolidation |
| **Memory bloat** | Any `.md` >200 lines | Recommend split into topic files |
| **Memory overlap** | Same topic in repo + user memory | Recommend single source of truth |
| **Thin categories** | Category with only 1 skill | Consider merging into parent |
| **Stale signals** | >50 unprocessed signals in pending-reviews/ | Warn about signal backlog |

> **Note on raw count thresholds**: Total skill count and per-category count limits
> (previously 350/50) have been removed. A large, well-indexed skill library is not
> a problem — stale and unreferenced skills are. Staleness detection requires the
> knowledge graph (WRK-205: `SKILLS_GRAPH.yaml` + `capabilities:`/`requires:`/`see_also:`
> frontmatter) to be effectively maintained. If the index is sparse, staleness signals
> will be noisy — assess index quality first.

**Knowledge graph maintenance** (when `SKILLS_GRAPH.yaml` exists — WRK-205):
- For any skill created or enhanced this session: verify it appears in `SKILLS_GRAPH.yaml`
- For any new relationship surfaced (A composes B, A requires B, A is alternative to B): add edge to graph
- For each new/enhanced skill: check that existing related skills have it in their `related_skills:` frontmatter (bidirectional linking); add missing links
- Update `last_used` timestamp in frontmatter for any skill loaded this session
- Flag skills missing `capabilities:`, `requires:`, or `see_also:` blocks for metadata enrichment

> **Prerequisite**: Graph maintenance only runs when `SKILLS_GRAPH.yaml` exists at `.claude/skills/`. Skip silently if absent — WRK-205 implements the graph.

**Outputs:**
- List of consolidation recommendations (skill merges, memory splits)
- List of new skill candidates (gaps identified from session patterns)
- Responsibility reallocation suggestions (e.g., "move X from memory to rules")
- Knowledge graph updates: edges added, `last_used` timestamps written, missing links added
- Metrics: total_skills, archived_ratio, avg_category_size, memory_total_lines

**Decision rules:**
- Consolidation: Only recommend if both skills have been loaded in same session 3+ times
- New skills: Only when pattern seen 3+ sessions AND no existing skill covers it
- Reallocation: Only when content clearly belongs to a different target (e.g., repeated correction → rules, not memory)

### Phase 4: GUARD — Safety Checks Before Writing (incl. ecosystem review outputs)

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

### Phase 5: APPLY — Write Improvements

**CLAUDE.md**: Resource Index scan, Core Rules for patterns confirmed 3+ sessions. Use Edit tool.

**Rules files** (`.claude/rules/*.md`): Add examples from real corrections. Append to sections, never restructure.

**Repo memory** (`.claude/memory/`): Add debugging lessons, tool conventions, API quirks. Use env var placeholders for paths. Create new topic file if section exceeds 10 entries.

**Skills** (`.claude/skills/**/*.md`) — FULL LIFECYCLE:
- **Enhance**: Add examples, fix instructions from corrections
- **Create**: New SKILL.md when repeated pattern has no matching skill
- **Deprecate**: Add deprecation notice when unused 90+ days
- **Archive**: Move to `_archive/` with reason and date

**Docs** (`.claude/docs/`): Update stale references, add missing documentation.

### Phase 6: LOG — Record Changes

Write to `.claude/state/improve-changelog.yaml`:
- Timestamp, changes list with file/action/diff_summary
- Skills lifecycle metrics: created/enhanced/deprecated/archived counts
- Ecosystem health metrics: total_skills, memory_lines, consolidation_count, reallocation_count
- signals_processed, changes_applied, signals_skipped (with reason)

### Phase 7: CLEANUP — Mark Signals Consumed

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
1. Search `.claude/skills/**/*.md` for existing coverage
2. If no match, create at `.claude/skills/<category>/<subcategory>/<name>/SKILL.md`
3. Follow existing SKILL.md template (YAML frontmatter + markdown sections)
4. Mark as `auto_generated: true` in frontmatter
5. Log in changelog with source pattern evidence

### Enhancing Existing Skills
1. Read current SKILL.md
2. Identify section to update (Quick Reference, examples, error handling)
3. Apply surgical edit (append examples, fix instructions)
4. Bump patch version in frontmatter
5. Log enhancement in changelog

### Deprecating Skills
1. Verify: no usage in last 90 days (check session logs, git history)
2. Verify: superseded by another skill (identify replacement)
3. Add to frontmatter: `deprecated: true`, `deprecated_date`, `replacement_skill`
4. Do NOT delete — archive in next pass

### Archiving Skills
1. Move from `.claude/skills/<category>/` to `.claude/skills/_archive/<category>/`
2. Add archive metadata: `archive_date`, `reason`, `original_path`
3. Update any cross-references in other skills

## Integration

- **Consumes** `/reflect` output from `.claude/state/patterns/`
- **Consumes** `/insights` output from session reports
- **Complements** session hooks (`capture-corrections.sh` produces signals)
- **Does NOT duplicate**: `/reflect` analyzes git history, `/improve` acts on signals

## Scope

| Target | Syncs via git? | Notes |
|---|---|---|
| Skill + command files | Yes | All users get the skill |
| CLAUDE.md, rules, docs | Yes | Shared improvements |
| `.claude/memory/` | Yes | Shared institutional knowledge |
| `.claude/skills/**/*.md` | Yes | Skill improvements shared |
| `.claude/state/` | No (gitignored) | Per-machine audit trail |

## Related Commands

- `/reflect` — Periodic reflection on git history
- `/insights` — Session analysis reports
- `/knowledge` — Knowledge capture and retrieval

## Script Mode (v1.2.0)

When invoked from the stop hook (session exit), `/improve` dispatches to `scripts/improve/improve.sh`:

- **Full mode** (`/exit`): All 7 phases run, including 2-3 Anthropic API calls (~30-60s)
- **Quick mode** (`--quick`): Shell-only phases (1, 3a, 4, 6, 7), skips API calls (~2-3s)
- **Dry run** (`--dry-run`): All phases execute but no files are written

The script uses the Anthropic Messages API directly (via `curl`) instead of `claude -p` to avoid nested session errors. Authentication uses OAuth token from `~/.claude/.credentials.json` with fallback to `ANTHROPIC_API_KEY` environment variable.

### Manual vs Automatic Invocation

| Mode | Trigger | Engine | AI Quality |
|------|---------|--------|------------|
| Manual | `/improve` command | Claude session (full reasoning) | Highest — full context |
| Automatic | Stop hook at session exit | `improve.sh` + API calls | Good — structured prompts |
| Quick | Ctrl+C or `--quick` | `improve.sh` shell-only | None — metrics + logging only |
