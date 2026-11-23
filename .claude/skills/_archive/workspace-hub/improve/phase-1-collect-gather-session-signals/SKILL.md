---
name: improve-phase-1-collect-gather-session-signals
description: "Sub-skill of improve: Phase 1: COLLECT \u2014 Gather Session Signals\
  \ (+6)."
version: 1.4.0
category: workspace-hub
type: reference
scripts_exempt: true
---

# Phase 1: COLLECT — Gather Session Signals (+6)

## Phase 1: COLLECT — Gather Session Signals


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


## Phase 2: CLASSIFY — Route Improvements to Targets


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


## Phase 3: ECOSYSTEM REVIEW — Structural Health Assessment


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
| **Stub micro-skills** | Stage micro-skill file < 15 lines | Flag as enhancement candidate — stubs provide no guidance at stage entry |

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

**Proactive skill discovery** (when `SKILLS_GRAPH.yaml` exists — WRK-205 + WRK-215):

Four checks are run to actively surface gaps — not just react to session signals:

| Check | Trigger | What it finds |
|-------|---------|---------------|
| Broken `see_also:`/`requires:` refs | Every `/improve` run | Skills referenced in frontmatter but no matching SKILL.md exists = gap |
| WRK-domain coverage | Weekly `/reflect` | Active WRK `tags:`/`module:` with no matching skill domain = under-skilled domain |
| Enhancement priority queue | Weekly `/reflect` | Skills with empty `capabilities:` AND `last_used` within 30 days = high-priority stubs |
| Domain saturation heatmap | `/improve --scope skills --audit` | WRK-items ÷ skills per domain ratio — low ratio = under-skilled domain |

**Broken-ref scan (runs every session):**
1. For each SKILL.md frontmatter: extract all `see_also:` and `requires:` values
2. For each value: check that a SKILL.md exists at the referenced path
3. Any broken reference → emit gap candidate to `.claude/state/pending-reviews/skill-candidates.jsonl`
4. Dedup: only emit each gap once per 7 days (keyed by target path + date week)

**Enhancement priority queue (weekly, via `/reflect`):**
- Rank criteria: `see_also:` reference frequency (most-referenced-by-other-skills) as primary; `last_used` recency as tiebreaker
- Output: top-5 enhancement candidates appended to `.claude/state/pending-reviews/skill-candidates.jsonl` with `type: enhancement`

**Domain saturation heatmap (on-demand: `/improve --scope skills --audit`):**
- For each skill domain (using WRK-205 category indexes): count skills
- For each domain: count active WRK items with matching `module:` or `tags:`
- Compute ratio; flag domains where ratio < 0.5 (more than 2 WRK items per skill)
- Print summary table to stdout; do not write to state files

> **Prerequisite**: All proactive discovery checks skip silently when `SKILLS_GRAPH.yaml` is absent.
> Log: "Skill discovery deferred — WRK-205 graph not yet built."

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


## Phase 4: GUARD — Safety Checks Before Writing (incl. ecosystem review outputs)


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


## Phase 5: APPLY — Write Improvements


**CLAUDE.md**: Resource Index scan, Core Rules for patterns confirmed 3+ sessions. Use Edit tool.

**Rules files** (`.claude/rules/*.md`): Add examples from real corrections. Append to sections, never restructure.

**Repo memory** (`.claude/memory/`): Add debugging lessons, tool conventions, API quirks. Use env var placeholders for paths. Create new topic file if section exceeds 10 entries.

**Skills** (`.claude/skills/**/*.md`) — FULL LIFECYCLE:
- **Enhance**: Add examples, fix instructions from corrections
- **Create**: New SKILL.md when repeated pattern has no matching skill
- **Deprecate**: Add deprecation notice when unused 90+ days
- **Archive**: Move to `_archive/` with reason and date

**Docs** (`.claude/docs/`): Update stale references, add missing documentation.


## Phase 6: LOG — Record Changes


Write to `.claude/state/improve-changelog.yaml`:
- Timestamp, changes list with file/action/diff_summary
- Skills lifecycle metrics: created/enhanced/deprecated/archived counts
- Ecosystem health metrics: total_skills, memory_lines, consolidation_count, reallocation_count
- signals_processed, changes_applied, signals_skipped (with reason)


## Phase 7: CLEANUP — Mark Signals Consumed


Move processed signals from `pending-reviews/*.jsonl` to archive so they aren't reprocessed.
