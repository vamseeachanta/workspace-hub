---
wrk_id: WRK-1105
title: "Knowledge persistence architecture — work-done summaries, resource-intelligence, career learnings"
domain: harness/knowledge
complexity: complex
route: C
created_at: 2026-03-10
target_repos:
  - workspace-hub
status: draft
version: "1.0"
---

## Mission

Design and implement a structured knowledge persistence system that routes WRK completion learnings out of MEMORY.md into a queryable knowledge-base, integrates it with resource-intelligence Stage 2 and session-start, and seeds career domain expertise — so each session builds on what past sessions learned.

## What

1. **Diagnosis document** — trace why WRK-NNN ARCHIVED summaries land in MEMORY.md (call-site audit)
2. **Architecture ADR** — knowledge routing table: each knowledge type → correct destination
3. **`scripts/knowledge/`** — three scripts: `capture-wrk-summary.sh`, `query-knowledge.sh`, `build-knowledge-index.sh`
4. **`knowledge-base/`** — persistent store: `wrk-completions.jsonl`, `career-learnings.yaml`, `index.jsonl`
5. **Integration hooks** — archive-item.sh (post-archive capture), resource-intelligence SKILL.md (category 10), session-start SKILL.md (Step 2 enrichment)
6. **Migration script** — `scripts/knowledge/migrate-memory-to-knowledge.sh` — moves WRK ARCHIVED summaries from MEMORY.md to knowledge-base
7. **MEMORY.md slimmed** — ≤150 lines, pointers only
8. **Career learnings seed** — initial engineering/finance/software entries in career-learnings.yaml (sourced from engineering-modules.md, legal-scanned before commit)
9. **≥5 TDD tests** in `scripts/knowledge/tests/`

## Why

MEMORY.md has grown to 146/200 lines, with ~25 WRK-NNN ARCHIVED entries. These accumulate because the orchestrator writes summaries manually during sessions — no script captures them at archive time. When compact-memory.py hits the line limit, these learnings are evicted and permanently lost. Engineering domain expertise (OrcaFlex, FEA, CFD, pipeline integrity, energy economics) exists nowhere in the system. Each session rediscovers patterns already learned. Resource-intelligence Stage 2 mines skills/docs but not a knowledge base. Fixing this end-to-end makes each session measurably more capable than the last.

## Acceptance Criteria

- [ ] AC-1: Diagnosis document (`assets/WRK-1105/diagnosis.md`) explaining why WRK summaries land in MEMORY.md
- [ ] AC-2: Architecture ADR (`assets/WRK-1105/knowledge-routing-adr.md`) with knowledge routing table
- [ ] AC-3: `scripts/knowledge/capture-wrk-summary.sh` — writes JSONL entry to knowledge-base/ at archive time (best-effort, non-blocking)
- [ ] AC-4: `scripts/knowledge/query-knowledge.sh` — query by keyword/domain, returns markdown output
- [ ] AC-5: `scripts/knowledge/build-knowledge-index.sh` — builds knowledge-base/index.jsonl from all stores
- [ ] AC-6: `archive-item.sh` calls capture-wrk-summary.sh as best-effort hook after gate pass
- [ ] AC-7: resource-intelligence SKILL.md updated with category 10 (knowledge-base query)
- [ ] AC-8: session-start SKILL.md updated with knowledge surfacing in Step 2
- [ ] AC-9: MEMORY.md ≤150 lines (pointers only) after migration
- [ ] AC-10: career-learnings.yaml seeded with ≥10 engineering/finance/software entries
- [ ] AC-11: ≥5 TDD tests pass in `scripts/knowledge/tests/`
- [ ] AC-12: `check-all.sh` passes (ruff + mypy if any Python; shellcheck on bash scripts)
- [ ] AC-13: Legal scan passes on all committed content

## Phases

### Phase 1 — Diagnosis & Architecture

**Objective:** Confirm the exact call-site that writes WRK summaries to MEMORY.md; define the knowledge routing table.

**Tasks:**
- 1.1 Audit session logs, MEMORY.md write patterns, and auto-memory rules to confirm WRK summaries are written by the orchestrator (not scripts)
- 1.2 Read compact-memory.py to confirm it evicts done-WRK entries without preservation
- 1.3 Write `assets/WRK-1105/diagnosis.md` — precise call-site, trigger mechanism, current fate of evicted entries
- 1.4 Write `assets/WRK-1105/knowledge-routing-adr.md` — routing table with rationale for each knowledge type
- 1.5 Define `knowledge-base/` JSONL schema for wrk-completions.jsonl and career-learnings.yaml

**Deliverables:**
- `assets/WRK-1105/diagnosis.md`
- `assets/WRK-1105/knowledge-routing-adr.md`
- JSONL schema (embedded in ADR)

**Exit Criteria:**
- Diagnosis confirmed: WRK summaries enter MEMORY.md via orchestrator auto-memory, not scripts
- Routing table covers all 6 knowledge types from the WRK item

---

### Phase 2 — Core Knowledge Scripts (TDD)

**Objective:** Implement capture, query, and index scripts with tests-first.

**Tasks:**
- 2.1 Write failing tests for capture-wrk-summary.sh (happy path, non-existent WRK, missing knowledge-base dir)
- 2.2 Implement `scripts/knowledge/capture-wrk-summary.sh` to pass tests
- 2.3 Write failing tests for query-knowledge.sh (keyword match, domain filter, empty result)
- 2.4 Implement `scripts/knowledge/query-knowledge.sh`
- 2.5 Write failing tests for build-knowledge-index.sh (index creation, incremental update)
- 2.6 Implement `scripts/knowledge/build-knowledge-index.sh`
- 2.7 Create `knowledge-base/` directory with `.gitkeep`; add `knowledge-base/*.jsonl` to `.gitignore` (runtime data)

**Deliverables:**
- `scripts/knowledge/capture-wrk-summary.sh`
- `scripts/knowledge/query-knowledge.sh`
- `scripts/knowledge/build-knowledge-index.sh`
- `scripts/knowledge/tests/` (≥5 tests)
- `knowledge-base/.gitkeep`

**Exit Criteria:**
- ≥5 TDD tests pass
- Scripts are shellcheck-clean

---

### Phase 3 — Integration

**Objective:** Wire knowledge capture into archive flow; enrich resource-intelligence and session-start.

**Tasks:**
- 3.1 Add best-effort capture hook to `scripts/work-queue/archive-item.sh` (after gate pass, before archive move)
- 3.2 Update `.claude/skills/workspace-hub/resource-intelligence/SKILL.md` — add category 10 (knowledge-base query) to Mining Checklist
- 3.3 Update `.claude/skills/workspace-hub/session-start/SKILL.md` — add Step 2b: query knowledge-base for relevant entries matching today's WRK items
- 3.4 Update `scripts/memory/compact-memory.py` — route done-WRK entries to knowledge-base/ before evicting them (AC-9 enabler)
- 3.5 Codex cross-review of skill changes (resource-intelligence, session-start)

**Deliverables:**
- Updated `archive-item.sh`
- Updated `resource-intelligence/SKILL.md`
- Updated `session-start/SKILL.md`
- Updated `compact-memory.py`

**Exit Criteria:**
- archive-item.sh integration test: archiving a WRK creates a knowledge-base entry
- resource-intelligence SKILL.md Codex-reviewed APPROVE or MINOR
- session-start SKILL.md Codex-reviewed APPROVE or MINOR

---

### Phase 4 — Migration & Career Learnings

**Objective:** Slim MEMORY.md and seed career domain expertise.

**Tasks:**
- 4.1 Write `scripts/knowledge/migrate-memory-to-knowledge.sh` — identifies WRK-NNN ARCHIVED lines in MEMORY.md, converts to JSONL entries, removes from MEMORY.md
- 4.2 Run migration in dry-run mode, verify output
- 4.3 Run migration for real; verify MEMORY.md ≤150 lines
- 4.4 Seed `knowledge-base/career-learnings.yaml` from engineering-modules.md (≥10 entries covering OrcaFlex, FEA/CFD, pipeline integrity, energy economics, software patterns)
- 4.5 Run `scripts/legal/legal-sanity-scan.sh` on career-learnings.yaml (must pass before commit)
- 4.6 Verify `eval-memory-quality.py` pct_done_wrk ≈ 0 and memory_md_headroom > 50 after migration

**Deliverables:**
- `scripts/knowledge/migrate-memory-to-knowledge.sh`
- Updated `MEMORY.md` (≤150 lines)
- `knowledge-base/career-learnings.yaml` (≥10 entries)

**Exit Criteria:**
- MEMORY.md line count ≤150
- eval-memory-quality.py memory_md_headroom > 50
- Legal scan passes on career-learnings.yaml

---

## Pseudocode

### capture-wrk-summary.sh
```
function capture_wrk_summary(wrk_id) → exit 0 (best-effort, non-blocking)
  wrk_file = pending/ or archive/ WRK-NNN.md
  if wrk_file not found: log warning, exit 0
  title = parse frontmatter title from wrk_file
  category = parse frontmatter category/subcategory from wrk_file
  archived_at = current ISO 8601 timestamp
  mission = extract ## Mission section body from wrk_file
  patterns = []
  if evidence/resource-intelligence.yaml exists:
    patterns = top_p2_gaps + constraints from yaml
  if evidence/future-work.yaml exists:
    follow_ons = recommendations[].id list
  ensure knowledge-base/ dir exists (mkdir -p, exit 0 on failure)
  entry = {"id": wrk_id, "title": title, "category": category,
           "archived_at": archived_at, "mission": mission,
           "patterns": patterns, "follow_ons": follow_ons}
  append JSON line to knowledge-base/wrk-completions.jsonl (flock for atomicity)
  exit 0
```

### query-knowledge.sh
```
function query-knowledge(--query Q, --domain D, --limit N) → markdown to stdout
  entries = []
  for each JSONL file in knowledge-base/:
    load all entries
  if --domain: filter entries where category matches D
  if --query: score each entry (count Q keyword occurrences in title+mission+patterns)
  sort by score desc, take top N (default 5)
  for each entry:
    print "## WRK-ID: title"
    print "Category: X | Archived: Y"
    print mission (truncated to 150 chars)
    if patterns: print patterns list
    if follow_ons: print follow-ons list
  if no entries: print "No knowledge entries found."
  exit 0
```

### migrate-memory-to-knowledge.sh
```
function migrate_memory_to_knowledge(--dry-run) → updates MEMORY.md + knowledge-base/
  lines = read MEMORY.md
  to_migrate = []
  to_keep = []
  for each line in lines:
    if line matches "**WRK-NNN ARCHIVED**" pattern (archived WRK summary line):
      to_migrate.append(line)
    else:
      to_keep.append(line)
  if dry-run:
    print "Would migrate N lines, keeping M lines"
    exit 0
  for each archived_line in to_migrate:
    parse wrk_id, title, hash from archived_line
    entry = {"id": wrk_id, "title": title, "source": "memory-migration", ...}
    append to knowledge-base/wrk-completions.jsonl
  write to_keep lines to MEMORY.md (atomic via tmp file + mv)
  print "Migrated N entries. MEMORY.md now M lines."
  exit 0
```

## Tests / Evals

| Test | Type | Expected |
|------|------|----------|
| `test_capture_happy_path` | happy | WRK completion entry appended to knowledge-base/wrk-completions.jsonl with correct fields |
| `test_capture_nonexistent_wrk` | edge | Script exits 0 (non-blocking), logs warning, no knowledge-base write |
| `test_capture_creates_knowledge_dir` | edge | If knowledge-base/ missing, creates it and writes entry |
| `test_query_domain_filter` | happy | `--domain harness` returns only entries with harness category |
| `test_query_empty_result` | edge | No matching entries → clean "No knowledge entries found." output, exit 0 |
| `test_migrate_dry_run` | happy | Dry-run counts correct N lines to migrate, does not modify MEMORY.md |
| `test_migrate_reduces_memory_lines` | happy | Post-migration MEMORY.md has fewer lines, WRK ARCHIVED summaries removed |

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| career-learnings.yaml contains client identifiers | Medium | High | Legal scan mandatory before commit (AC-13) |
| archive-item.sh hook stalls archive gate on failure | Low | High | Best-effort hook: redirect stderr to log, always exit 0 |
| compact-memory.py routing change drops valid entries | Medium | Medium | Dry-run test before applying; TDD test covers migration path |
| SKILL.md updates require Codex gate (takes session time) | High | Low | Plan for it; Codex fallback to Claude Opus per quota policy |
| knowledge-base JSONL grows unbounded | Low | Low | Add nightly index rebuild; capture size in eval-memory-quality.py |

## Out of Scope

- Vector embeddings or semantic search (not yet needed; JSONL with keyword search is sufficient for Phase 1)
- Cross-machine knowledge sync (ace-linux-2, acma-ansys05) — knowledge-base/ lives on ace-linux-1 only
- Automated career learnings extraction from engineering session logs (manual seed only in this WRK)
- Retroactive backfill of all archived WRK items from git history (migrate MEMORY.md entries only)

## Standards References

- `.claude/rules/coding-style.md` — shellcheck clean, snake_case, 400L file limit
- `.claude/rules/testing.md` — TDD mandatory, ≥5 tests
- `.claude/rules/legal-compliance.md` — legal scan on career-learnings.yaml
- `.claude/rules/git-workflow.md` — feature/ branch, conventional commits
- `.claude/rules/patterns.md` — scripts over LLM judgment; no god objects
- `.claude/docs/orchestrator-pattern.md` — delegation, checkpoint/resume

## Plan Review Confirmation

confirmed_by: <!-- reviewer name, e.g. "vamsee" -->
confirmed_at: <!-- ISO-8601 timestamp -->
decision: <!-- passed | changes-requested -->
notes: <!-- optional -->
