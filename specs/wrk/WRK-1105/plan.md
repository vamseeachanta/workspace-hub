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
7. **MEMORY.md slimmed** — ≤80 lines (target 50–70), pointers only
8. **Career learnings seed** — initial engineering/finance/software entries in career-learnings.yaml (sourced from engineering-modules.md, legal-scanned before commit)
9. **≥16 TDD tests** in `scripts/knowledge/tests/`

## Why

MEMORY.md has grown to 146/200 lines, with ~25 WRK-NNN ARCHIVED entries. These accumulate because the orchestrator writes summaries manually during sessions — no script captures them at archive time. When compact-memory.py hits the line limit, these learnings are evicted and permanently lost. Engineering domain expertise (OrcaFlex, FEA, CFD, pipeline integrity, energy economics) exists nowhere in the system. Each session rediscovers patterns already learned. Resource-intelligence Stage 2 mines skills/docs but not a knowledge base. Fixing this end-to-end makes each session measurably more capable than the last.

## Acceptance Criteria

- [ ] AC-1: Diagnosis document (`assets/WRK-1105/diagnosis.md`) explaining why WRK summaries land in MEMORY.md
- [ ] AC-2: Architecture ADR (`assets/WRK-1105/knowledge-routing-adr.md`) with knowledge routing table
- [ ] AC-3: `scripts/knowledge/capture-wrk-summary.sh` — writes JSONL entry to knowledge-base/ at archive time (best-effort, non-blocking)
- [ ] AC-4: `scripts/knowledge/query-knowledge.sh` — query by keyword/domain, returns markdown output
- [ ] AC-5: `scripts/knowledge/build-knowledge-index.sh` — builds knowledge-base/index.jsonl from all stores
- [ ] AC-6: `archive-item.sh` calls capture-wrk-summary.sh as best-effort hook **after the archive move succeeds** (`|| true` — never blocks); duplicate check and append inside same flock section
- [ ] AC-7: resource-intelligence SKILL.md updated with category 10 (knowledge-base query)
- [ ] AC-8: session-start SKILL.md updated with knowledge surfacing in Step 2
- [ ] AC-9: MEMORY.md ≤80 lines (active state + pointers only) after migration — target 50–70 lines
- [ ] AC-10: `knowledge/seeds/career-learnings.yaml` (committed) seeded with ≥10 engineering/finance/software entries
- [ ] AC-11: ≥16 TDD tests pass in `scripts/knowledge/tests/` (covering: happy path, non-existent WRK, dir creation, flock contention, malformed YAML, corrupt JSONL skip, empty result, migrate dry-run, migrate reduces lines, concurrent cron guard, and more)
- [ ] AC-12: `shellcheck scripts/knowledge/*.sh` passes; `uv run --no-project python -m mypy scripts/memory/compact-memory.py` passes (note: `check-all.sh` targets tier-1 Python repos only, not hub scripts)
- [ ] AC-13: Legal scan passes on all committed content

## Phases

### Phase 1 — Diagnosis & Architecture

**Objective:** Confirm the exact call-site that writes WRK summaries to MEMORY.md; define the knowledge routing table.

**Tasks:**
- 1.1 Audit session logs, MEMORY.md write patterns, and auto-memory rules to confirm WRK summaries are written by the orchestrator (not scripts)
- 1.2 Read compact-memory.py to confirm it evicts done-WRK entries without preservation
- 1.3 Write `assets/WRK-1105/diagnosis.md` — precise call-site, trigger mechanism, current fate of evicted entries
- 1.4 Write `assets/WRK-1105/knowledge-routing-adr.md` — routing table with rationale for each knowledge type
- 1.5 Define canonical JSONL schema in the ADR: `id`, `type` (`wrk|career`), `category`, `subcategory`, `title`, `archived_at` (or `learned_at`), `source`, `mission` (WRK) or `context` (career), `patterns`, `follow_ons`. WRK entries: `id = "WRK-NNN"`, `type = "wrk"`, `category/subcategory` from WRK frontmatter. Career entries: `id = "CAREER-<domain>-<slug>"` (e.g. `CAREER-engineering-orcaflex-viv`), `type = "career"`. The `type` field enables display and dedup separation. query-knowledge.sh renders career entries as `## CAREER-slug: title` (not `## WRK-ID`). The spec file's `domain:` metadata is not used by capture scripts — WRK frontmatter `category`/`subcategory` fields are canonical.
- 1.6 Define persistence layers in ADR:
    - **committed seed**: `knowledge/seeds/career-learnings.yaml` (tracked, legal-reviewed source of truth for career domain knowledge)
    - **machine-local runtime**: `knowledge-base/` (gitignored) — generated JSONL (wrk-completions.jsonl, index.jsonl) rebuilt from archive/ history; not committed
    - Note: MEMORY.md in this WRK = `/home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/MEMORY.md` (Claude auto-memory, outside repo, writable by Claude Code agents — no sandbox restriction) — distinct from `.claude/memory/KNOWLEDGE.md` (in-repo institutional memory)
    - ADR must include rebuild command: if knowledge-base/ is lost after migration, run `bash scripts/knowledge/rebuild-from-archive.sh` to reconstruct wrk-completions.jsonl from .claude/work-queue/archive/**/*.md (future-work follow-on WRK captured in Stage 15)

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
- 2.7 Create `knowledge-base/` directory with `.gitkeep`; add `knowledge-base/*.jsonl` and `knowledge-base/index.jsonl` and `knowledge-base/*.lock` to `.gitignore` — these are machine-local runtime state, not committed artifacts. Persistence rationale: knowledge-base is local to ace-linux-1 and rebuilt from archive/ history if lost.

**Deliverables:**
- `scripts/knowledge/capture-wrk-summary.sh`
- `scripts/knowledge/query-knowledge.sh`
- `scripts/knowledge/build-knowledge-index.sh`
- `scripts/knowledge/tests/` (≥13 Phase-2 tests)
- `knowledge-base/.gitkeep`

**Exit Criteria:**
- Phase 2 tests pass (≥13 tests: capture ×6, query ×4, index ×3 — Phase 3/4 tests run after those phases)
- Scripts are shellcheck-clean

---

### Phase 3 — Integration

**Objective:** Wire knowledge capture into archive flow; enrich resource-intelligence and session-start.

**Tasks:**
- 3.1 Add best-effort capture hook to `scripts/work-queue/archive-item.sh` — hook runs **after the archive move succeeds** (not before) so knowledge-base only records completed archives. Hook uses `|| true` (never blocks archive gate).
- 3.2 Update `.claude/skills/workspace-hub/resource-intelligence/SKILL.md` — add category 10 (knowledge-base query) to Mining Checklist
- 3.3 Update `.claude/skills/workspace-hub/session-start/SKILL.md` — add Step 2b: query knowledge-base for relevant entries matching today's WRK items
- 3.4 Update `scripts/memory/compact-memory.py` — extend the trim rule to also detect and route WRK ARCHIVED bullets IN MEMORY.md to knowledge-base/ before silently discarding them. Note: compact-memory.py currently reads MEMORY.md for line counting (line 123) but skips it in `_read_topic_files()` — the extension must add a WRK ARCHIVED bullet extractor for MEMORY.md specifically. After change: run existing 21 compact-memory TDD tests as regression gate.
- 3.5 Wire `scripts/knowledge/*.sh` into `check-all.sh` (shellcheck path); add compact-memory.py Python changes to mypy check path.
- 3.6 Codex cross-review of ALL implementation changes — scripts (capture/query/index/archive hook), compact-memory.py routing, migration flow, and skill docs (resource-intelligence, session-start) — per Route C mandatory cross-review requirement

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
- 4.1 Write `scripts/knowledge/migrate-memory-to-knowledge.sh` — block-aware parser, auto-backup MEMORY.md before any destructive write (MEMORY.md.bak), atomic tmp+mv write, rollback path if append fails midway. Fixture tests must cover ≥3 real MEMORY block shapes before non-dry-run step.
- 4.2 Run migration in dry-run mode, verify output
- 4.3 Run migration for real; verify MEMORY.md ≤80 lines
- 4.4 Seed `knowledge/seeds/career-learnings.yaml` (committed source) from engineering-modules.md (≥10 entries). build-knowledge-index.sh reads this file and normalizes into knowledge-base/ runtime store.
- 4.5 Run `git add knowledge/seeds/career-learnings.yaml && scripts/legal/legal-sanity-scan.sh --diff-only` on career-learnings.yaml (must pass before commit; --diff-only scans staged changes)
- 4.6 Verify MEMORY.md line count directly: `wc -l MEMORY.md` ≤80 after migration. Note: eval-memory-quality.py pct_done_wrk counts `status: done` items (topic files) — does not detect MEMORY.md ARCHIVED bullets. Use direct line count as the acceptance signal.

**Deliverables:**
- `scripts/knowledge/migrate-memory-to-knowledge.sh`
- Updated `MEMORY.md` (≤80 lines, target 50–70)
- `knowledge/seeds/career-learnings.yaml` (committed, ≥10 entries, legal-reviewed)

**Exit Criteria:**
- MEMORY.md line count ≤80 (target 50–70)
- `wc -l MEMORY.md` ≤80 (direct line count — eval-memory-quality.py pct_done_wrk not suitable for this check)
- Legal scan passes on career-learnings.yaml

---

## Pseudocode

### capture-wrk-summary.sh
```
function capture_wrk_summary(wrk_id) → exit 0 (best-effort, non-blocking)
  # WRK files exist in flat and YYYY-MM-sharded layouts
  wrk_file = find_first([
    ".claude/work-queue/pending/WRK-NNN.md",
    ".claude/work-queue/archive/WRK-NNN.md",              # flat legacy
    ".claude/work-queue/archive/*/WRK-NNN.md",            # YYYY-MM sharded
    ".claude/work-queue/done/WRK-NNN.md",
  ])
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
function query-knowledge(--query Q, --category C, --limit N) → markdown to stdout
  # Prefer index.jsonl when source files have mtime <= index.jsonl mtime
  if index.jsonl exists and all source files mtime <= index.jsonl mtime
     (source files = wrk-completions.jsonl AND knowledge/seeds/career-learnings.yaml):
    load entries from index.jsonl
  else:
    load entries from all *.jsonl in knowledge-base/ + normalize career-learnings.yaml
  if --category: filter entries where entry.category matches C
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
  # MEMORY.md WRK entries are SINGLE-LINE bullets (confirmed from actual file):
  # Format: "- **WRK-NNN ARCHIVED** (hash): title/summary..."
  # No multi-line accumulation needed — each bullet is self-contained.

  entries_to_migrate = []
  keep_lines = []

  for each line in MEMORY.md:
    if line matches r'^\s*-\s+\*\*WRK-(\d+)\s+ARCHIVED\*\*' pattern:
      wrk_id = match[1]
      entries_to_migrate.append({wrk_id: "WRK-"+wrk_id, raw: line})
    else:
      keep_lines.append(line)

  if dry-run:
    print "Would migrate N lines (preview first 3 entries)"
    print "keep_lines count: M"
    exit 0

  # Backup MEMORY.md before writing
  cp MEMORY.md MEMORY.md.bak

  for each entry in entries_to_migrate:
    append_if_new(entry.wrk_id, {id: entry.wrk_id, source: "memory-migration", raw: entry.raw}, wrk-completions.jsonl)

  # Atomic write of kept lines
  write keep_lines to MEMORY.md.tmp; mv MEMORY.md.tmp MEMORY.md
  print "Migrated N entries. MEMORY.md now M lines."
  exit 0
```

### Idempotency contract (all capture paths)
```
# Duplicate check MUST happen inside the same flock-protected section as the append.
# A read-check-append outside the lock creates a race: two concurrent archivers
# both observe "id missing" and both append.

function append_if_new(wrk_id, entry, jsonl_path):
  (
    flock -w 5 200 || { log "lock timeout, skip"; exit 0; }
    existing_ids = {jq -r .id jsonl_path | sort | uniq}
    if wrk_id in existing_ids:
      log "Skipping WRK-{wrk_id} — already in knowledge-base"
    else:
      echo entry_json >> jsonl_path
  ) 200>{jsonl_path}.lock

This pattern applies to capture-wrk-summary.sh, compact-memory.py routing, and
migrate-memory-to-knowledge.sh.
```

### build-knowledge-index.sh (normalizes all stores → index.jsonl)
```
function build_knowledge_index() → writes knowledge-base/index.jsonl (exclusive lock)
  acquire flock on knowledge-base/.index.lock (timeout 30s, exit 0 if lock unavailable)
  entries = []
  for each *.jsonl in knowledge-base/ (except index.jsonl):
    load and append all valid JSON lines (skip malformed lines with warning)
  for each entry in career-learnings.yaml (normalize to JSONL schema):
    append normalized entry
  remove duplicate entries by id (keep first occurrence)
  write all entries to knowledge-base/index.jsonl (atomic: tmp + mv)
  release lock
  exit 0

Note: Each write path (capture-wrk-summary.sh, compact-memory routing, migration, career seed)
calls build-knowledge-index.sh after writing to keep index current. query-knowledge.sh
uses index.jsonl when present AND when all source files have mtime <= index.jsonl mtime
(source-mtime comparison, not fixed 24h window). Falls back to scanning raw JSONL directly
when index is stale or absent. This makes career-learnings.yaml queryable through the
same path as WRK completions.
```

## Tests / Evals

| Phase | Test | Type | Expected |
|-------|------|------|----------|
| P2 | `test_capture_happy_path` | happy | WRK entry appended to wrk-completions.jsonl with correct fields |
| P2 | `test_capture_nonexistent_wrk` | edge | Exits 0 (non-blocking), logs warning, no knowledge-base write |
| P2 | `test_capture_creates_knowledge_dir` | edge | Creates knowledge-base/ if missing, writes entry |
| P2 | `test_capture_idempotent` | edge | Re-running for same WRK-ID does not append duplicate |
| P2 | `test_capture_malformed_yaml` | error | Malformed resource-intelligence.yaml → patterns=[], entry still written |
| P2 | `test_capture_flock_timeout` | edge | Lock held by another process → exits 0 after flock timeout |
| P2 | `test_query_keyword_match` | happy | `--query pipeline` returns entries mentioning pipeline |
| P2 | `test_query_domain_filter` | happy | `--category harness` returns only harness-category entries |
| P2 | `test_query_empty_result` | edge | No matches → "No knowledge entries found." output, exit 0 |
| P2 | `test_query_corrupt_jsonl_skip` | error | Malformed JSONL line skipped, valid entries still returned |
| P2 | `test_index_builds_from_jsonl` | happy | index.jsonl contains all entries from wrk-completions.jsonl |
| P2 | `test_index_normalizes_career_learnings` | happy | career-learnings.yaml entries appear in index.jsonl |
| P2 | `test_index_deduplicates` | edge | Duplicate id in multiple JSONL files → single entry in index |
| P3 | `test_archive_hook_writes_knowledge` | happy | Archiving WRK creates knowledge-base entry without blocking |
| P3 | `test_compact_memory_routes_before_evict` | happy | compact-memory.py routes done-WRK entries to knowledge-base/ before removing them |
| P4 | `test_migrate_dry_run` | happy | Dry-run previews N blocks to migrate, does not modify MEMORY.md |
| P4 | `test_migrate_reduces_memory_lines` | happy | Post-migration MEMORY.md ≤80 lines, WRK ARCHIVED blocks removed |
| P4 | `test_migrate_idempotent` | edge | Re-running migration skips already-captured WRK IDs |

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
