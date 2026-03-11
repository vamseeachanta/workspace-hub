OpenAI Codex v0.112.0 (research preview)
--------
workdir: /mnt/local-analysis/workspace-hub
model: gpt-5.4
provider: openai
approval: never
sandbox: workspace-write [workdir, /tmp, $TMPDIR, /home/vamsee/.codex/memories]
reasoning effort: medium
reasoning summaries: none
session id: 019cd91c-9a19-7650-aeba-04a8e7948725
--------
user
# Stance: Codex Plan Draft Review

You are a software engineer agent. Your focus is on **implementation correctness, edge cases, and testability**.

You will receive a Claude-authored plan draft. Walk it section-by-section and produce your own refined version.

When reviewing:
1. Challenge any assumptions about implementation approach — is there a simpler or more robust way?
2. Identify edge cases not covered (malformed input, missing fields, timezone/date math, quota exhaustion).
3. Flag AC gaps — things implementable but not covered by the listed tests.
4. Assess integration risks (nightly cron, file writes, CLI availability).
5. Verify uv run --no-project python is used wherever Python is called.

Your output must be a complete refined plan (same structure as the input draft).
Add a "Codex Notes" section at the end with your specific findings.

---
CLAUDE DRAFT PLAN:
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
mcp startup: no servers
codex
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
version: "1.1-codex"
---

## Mission

Design and implement a structured, durable knowledge persistence system that routes WRK completion learnings out of `MEMORY.md` into a queryable knowledge base, integrates that knowledge into archive flow, resource-intelligence Stage 2, and session-start, and seeds reusable career/domain expertise so session learnings survive compaction and are practically discoverable.

## What

1. **Diagnosis document** — trace the actual write path that causes `WRK-NNN ARCHIVED` summaries to land in `MEMORY.md`, including whether the source is orchestrator behavior, session-exit behavior, or memory compaction side effects.
2. **Architecture ADR** — define a routing table for each knowledge type, storage format, ownership, read paths, and failure behavior.
3. **`scripts/knowledge/`** — implement:
   - `capture-wrk-summary.sh`
   - `query-knowledge.sh`
   - `build-knowledge-index.sh`
   - `migrate-memory-to-knowledge.sh`
4. **`knowledge-base/`** — persistent store:
   - `wrk-completions.jsonl`
   - `career-learnings.yaml`
   - `index.jsonl`
5. **Integration hooks** — archive capture in `scripts/work-queue/archive-item.sh`; knowledge lookup in resource-intelligence and session-start; compaction-safe handling for done-WRK entries.
6. **Migration path** — move only parseable archived WRK summary lines from `MEMORY.md` into the knowledge base with dry-run and idempotency.
7. **`MEMORY.md` slimmed** — keep it as a short working-memory artifact with pointers only; no archived WRK summaries after migration.
8. **Career learnings seed** — initial engineering/finance/software entries in `career-learnings.yaml`, curated and legal-scanned before commit.
9. **TDD coverage** — tests for parsing, duplicate capture, malformed data, empty stores, concurrent writes, and migration safety.
10. **Operational safeguards** — UTC timestamps, atomic writes, `flock` locking, graceful degradation when tools/files are missing, and `uv run --no-project python` for every Python invocation.

## Why

The core failure mode is not just that `MEMORY.md` is large; it is that archived WRK learnings are being stored in a lossy short-term medium with no durable handoff. Once compaction or manual cleanup removes them, the information becomes undiscoverable. That creates repeated re-learning cost, especially in engineering and workflow domains where patterns should compound over time.

The fix needs to be operationally safe. Archive flow cannot block, session-start cannot fail when the knowledge base is absent or malformed, compaction cannot silently drop data, and migration must be repeatable without duplicating entries. The solution therefore needs explicit routing rules, durable storage, idempotent capture, and tests around malformed input and integration boundaries.

## Acceptance Criteria

- [ ] AC-1: Diagnosis document at `assets/WRK-1105/diagnosis.md` identifies the exact write path(s), triggers, and why archived WRK summaries currently persist in `MEMORY.md`
- [ ] AC-2: ADR at `assets/WRK-1105/knowledge-routing-adr.md` defines routing table, schemas, ownership, read/write points, and failure semantics
- [ ] AC-3: `scripts/knowledge/capture-wrk-summary.sh` appends a deduplicated JSONL entry to `knowledge-base/wrk-completions.jsonl` as a best-effort, non-blocking hook
- [ ] AC-4: `scripts/knowledge/query-knowledge.sh` supports `--query`, `--domain`, and `--limit`, degrades cleanly on missing/empty stores, and returns markdown output
- [ ] AC-5: `scripts/knowledge/build-knowledge-index.sh` rebuilds `knowledge-base/index.jsonl` deterministically from all source stores
- [ ] AC-6: `scripts/work-queue/archive-item.sh` invokes capture after gate pass, never blocks archive completion if capture fails, and logs failures clearly
- [ ] AC-7: `.claude/skills/workspace-hub/resource-intelligence/SKILL.md` is updated to include a knowledge-base query step in Stage 2 mining
- [ ] AC-8: `.claude/skills/workspace-hub/session-start/SKILL.md` is updated to surface relevant prior knowledge during startup, with graceful fallback when knowledge data is missing
- [ ] AC-9: `MEMORY.md` contains no archived WRK summary entries after migration and remains at or below 150 lines
- [ ] AC-10: `knowledge-base/career-learnings.yaml` contains at least 10 vetted engineering/finance/software entries with stable schema
- [ ] AC-11: At least 8 tests pass under `scripts/knowledge/tests/`, including malformed input, duplicate capture, and migration dry-run cases
- [ ] AC-12: All Python execution in scripts/tests uses `uv run --no-project python ...`; no bare `python3` is introduced
- [ ] AC-13: Repository checks pass, including shell validation and any applicable Python checks for touched Python files
- [ ] AC-14: Legal scan passes on committed knowledge content, especially `career-learnings.yaml`
- [ ] AC-15: Capture and migration logic are idempotent: rerunning them does not create duplicate knowledge entries for the same source event

## Phases

### Phase 1 — Diagnosis & Architecture

**Objective:** Confirm the real write path for archived WRK summaries and define a robust storage/routing design before implementation.

**Tasks:**
- 1.1 Audit all call sites that can write or reshape `MEMORY.md`, including session orchestration, session-end/save flows, memory compaction, and any helper scripts
- 1.2 Confirm whether archived WRK entries are inserted at creation time, preserved by compaction, or recreated from another source
- 1.3 Inspect `scripts/memory/compact-memory.py` and any callers to determine how done-WRK entries are currently treated and whether preservation hooks already exist
- 1.4 Write `assets/WRK-1105/diagnosis.md` with concrete file/function references, trigger sequence, and evidence for the current behavior
- 1.5 Write `assets/WRK-1105/knowledge-routing-adr.md` defining:
  - knowledge categories
  - destination store per category
  - write-time vs rebuild-time ownership
  - schema/versioning
  - failure handling
  - retention and rebuild strategy
- 1.6 Define stable schemas for:
  - `wrk-completions.jsonl`
  - `career-learnings.yaml`
  - `index.jsonl`
- 1.7 Decide dedupe key strategy up front, preferably a stable `source_id` or `(wrk_id, archived_event_hash)` rather than title text

**Deliverables:**
- `assets/WRK-1105/diagnosis.md`
- `assets/WRK-1105/knowledge-routing-adr.md`
- Schemas embedded in ADR

**Exit Criteria:**
- The write path for archived WRK summaries is evidenced, not inferred
- ADR includes read/write ownership and idempotency rules
- Schema includes required/optional fields and malformed-input policy

---

### Phase 2 — Core Knowledge Scripts (TDD)

**Objective:** Implement core capture/query/index behavior with tests first and minimal parsing fragility.

**Tasks:**
- 2.1 Create failing tests for `capture-wrk-summary.sh`:
  - happy path
  - nonexistent WRK
  - missing `knowledge-base/`
  - malformed frontmatter or missing sections
  - duplicate capture attempt
  - concurrent append behavior
- 2.2 Implement `scripts/knowledge/capture-wrk-summary.sh`
  - shell wrapper preferred
  - if JSON/YAML parsing is needed, call `uv run --no-project python ...`
  - use `flock` and atomic append semantics
  - emit UTC ISO-8601 timestamps
  - exit `0` on operational failure after logging
- 2.3 Create failing tests for `query-knowledge.sh`:
  - keyword match
  - domain filter
  - limit handling
  - empty result
  - missing store files
  - malformed JSONL row tolerance
- 2.4 Implement `scripts/knowledge/query-knowledge.sh`
  - deterministic sort
  - tolerant reads
  - markdown output
  - exit `0` on empty/no-match cases
- 2.5 Create failing tests for `build-knowledge-index.sh`:
  - initial build
  - rebuild determinism
  - malformed source row skipped with warning
  - empty stores
- 2.6 Implement `scripts/knowledge/build-knowledge-index.sh`
  - prefer full rebuild over incremental mutation unless a measured need emerges
  - generate deterministic `index.jsonl`
- 2.7 Create `knowledge-base/` directory with `.gitkeep`
- 2.8 Update ignore rules so runtime JSONL artifacts are handled intentionally without hiding committed seed files such as `career-learnings.yaml`

**Deliverables:**
- `scripts/knowledge/capture-wrk-summary.sh`
- `scripts/knowledge/query-knowledge.sh`
- `scripts/knowledge/build-knowledge-index.sh`
- `scripts/knowledge/tests/`
- `knowledge-base/.gitkeep`

**Exit Criteria:**
- At least 6 script-level tests pass before integration work begins
- Scripts are shellcheck-clean
- No Python execution path uses bare `python3`

---

### Phase 3 — Integration

**Objective:** Wire knowledge capture into archive flow and knowledge surfacing into startup/research flows without introducing blocking failures.

**Tasks:**
- 3.1 Add a best-effort hook to `scripts/work-queue/archive-item.sh` after gate pass succeeds and before final archive move if source data must still be accessible; otherwise after move if archived file is the canonical source
- 3.2 Ensure archive integration logs failures but never changes archive exit status
- 3.3 Add an integration test covering archive flow creating a knowledge entry once, not multiple times on retry
- 3.4 Update `.claude/skills/workspace-hub/resource-intelligence/SKILL.md` to include knowledge-base lookup in Stage 2 mining, with fallback behavior if query tooling/store is unavailable
- 3.5 Update `.claude/skills/workspace-hub/session-start/SKILL.md` to surface relevant prior knowledge for current/top WRK items without making startup dependent on the knowledge store
- 3.6 Reassess `scripts/memory/compact-memory.py` change scope:
  - prefer a narrow preservation hook only if diagnosis proves compaction is a remaining loss vector
  - avoid coupling compaction to new store writes unless necessary
- 3.7 If `compact-memory.py` must be changed, add tests covering malformed lines, duplicate prevention, and no-op behavior when nothing is migratable
- 3.8 Complete cross-review for significant workflow/skill changes before closing implementation

**Deliverables:**
- Updated `scripts/work-queue/archive-item.sh`
- Updated `.claude/skills/workspace-hub/resource-intelligence/SKILL.md`
- Updated `.claude/skills/workspace-hub/session-start/SKILL.md`
- Updated `scripts/memory/compact-memory.py` only if required by diagnosis

**Exit Criteria:**
- Archive integration test passes
- Session-start/resource-intelligence behavior is explicitly non-fatal on missing or malformed knowledge data
- Cross-review verdict is `APPROVE` or `MINOR`

---

### Phase 4 — Migration & Career Learnings

**Objective:** Migrate durable archived knowledge out of `MEMORY.md`, seed reusable expertise, and verify the working-memory artifact stays lean.

**Tasks:**
- 4.1 Write failing tests for `migrate-memory-to-knowledge.sh`:
  - dry-run
  - real migration
  - malformed archived summary lines
  - duplicate migration rerun
  - atomic rewrite of `MEMORY.md`
- 4.2 Implement `scripts/knowledge/migrate-memory-to-knowledge.sh`
  - parse only recognized archived summary formats
  - skip ambiguous lines with warnings
  - use temp file + atomic move for `MEMORY.md`
  - use same dedupe strategy as capture
  - use `uv run --no-project python ...` for structured parsing if needed
- 4.3 Run migration in dry-run mode and inspect proposed counts
- 4.4 Run migration for real and verify `MEMORY.md` contains pointers only and remains within size target
- 4.5 Seed `knowledge-base/career-learnings.yaml` with at least 10 entries spanning engineering, finance, and software
- 4.6 Validate career-learning schema and run legal scan before commit
- 4.7 Run memory quality evaluation and confirm archived WRK noise is removed from working memory
- 4.8 Rebuild `knowledge-base/index.jsonl` after migration and seed creation

**Deliverables:**
- `scripts/knowledge/migrate-memory-to-knowledge.sh`
- Updated `MEMORY.md`
- `knowledge-base/career-learnings.yaml`
- Rebuilt `knowledge-base/index.jsonl`

**Exit Criteria:**
- `MEMORY.md` line count is `<= 150`
- Archived WRK summary lines are removed from `MEMORY.md`
- Migration is idempotent on rerun
- Legal scan passes on new committed knowledge content

---

## Pseudocode

### capture-wrk-summary.sh
```text
function capture_wrk_summary(wrk_id) -> exit 0
  resolve canonical wrk_file from pending/archive paths
  if wrk_file missing:
    warn and exit 0

  parse frontmatter + selected sections from wrk_file
  if required fields missing:
    warn, build partial entry if safe, else exit 0

  source_id = stable capture key derived from wrk_id + archive state
  archived_at = current UTC ISO-8601 timestamp

  collect optional enrichments:
    mission
    domain/category
    evidence-derived patterns
    follow_on ids

  mkdir -p knowledge-base or warn and exit 0
  open lock on wrk-completions.jsonl.lock
  if entry with same source_id already exists:
    exit 0

  append one JSON object line atomically to knowledge-base/wrk-completions.jsonl
  exit 0
```

### query-knowledge.sh
```text
function query_knowledge(--query Q, --domain D, --limit N=5) -> markdown stdout
  load records from known stores:
    wrk-completions.jsonl
    career-learnings.yaml
    optional index.jsonl if that is the canonical query source

  tolerate missing files
  skip malformed rows with warning to stderr

  normalize query/domain inputs
  filter by domain if provided
  score by keyword presence across title, mission, tags, patterns, learnings
  sort deterministically by score desc, then recency desc, then id asc
  take top N

  if none:
    print "No knowledge entries found."
    exit 0

  print markdown blocks with stable fields only
  exit 0
```

### build-knowledge-index.sh
```text
function build_knowledge_index() -> exit 0/nonzero on true build failure
  load all source stores
  skip malformed source rows with warning count
  normalize each record into common index schema
  sort deterministically
  write index to temp file
  atomically replace knowledge-base/index.jsonl
  exit 0
```

### migrate-memory-to-knowledge.sh
```text
function migrate_memory_to_knowledge(--dry-run) -> exit 0/nonzero on unsafe rewrite failure
  read MEMORY.md
  classify each line:
    migratable archived summary
    ambiguous archived-like line
    keep

  for migratable lines:
    derive stable source_id
    build entry payload tagged source="memory-migration"

  if dry-run:
    print counts: migrate / skip ambiguous / keep / duplicates
    exit 0

  append only non-duplicate entries to wrk-completions.jsonl under lock
  write kept lines back to MEMORY.md via temp file + mv
  rebuild index
  print summary counts
  exit 0
```

## Tests / Evals

| Test | Type | Expected |
|------|------|----------|
| `test_capture_happy_path` | happy | Appends one valid WRK completion entry with expected required fields |
| `test_capture_nonexistent_wrk` | edge | Exits `0`, logs warning, performs no write |
| `test_capture_creates_knowledge_dir` | edge | Creates missing `knowledge-base/` and writes entry |
| `test_capture_missing_required_fields` | edge | Handles malformed/missing frontmatter or mission safely without crashing |
| `test_capture_deduplicates_same_wrk_event` | edge | Repeated capture for same source event does not create duplicate rows |
| `test_capture_concurrent_writes` | edge | Parallel capture attempts do not corrupt JSONL |
| `test_query_domain_filter` | happy | `--domain` returns only matching entries |
| `test_query_limit_and_sort` | happy | `--limit` respects deterministic ranking |
| `test_query_empty_result` | edge | Prints clean no-result message, exits `0` |
| `test_query_skips_malformed_rows` | edge | Malformed JSONL rows are skipped with warning, valid rows still return |
| `test_build_index_deterministic_rebuild` | happy | Two rebuilds from same inputs produce identical index |
| `test_build_index_skips_bad_source_rows` | edge | Bad source rows do not fail whole build |
| `test_migrate_dry_run` | happy | Reports counts and does not modify files |
| `test_migrate_reduces_memory_lines` | happy | Real migration removes migratable archived lines from `MEMORY.md` |
| `test_migrate_idempotent_rerun` | edge | Second run creates no duplicates and leaves `MEMORY.md` unchanged |
| `test_archive_hook_best_effort` | integration | Archive completes even if capture hook fails |
| `test_archive_hook_writes_once` | integration | Archive flow creates exactly one knowledge entry for the WRK |

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Assumed write source is wrong; fix targets wrong layer | Medium | High | Phase 1 diagnosis must cite exact call site before implementation |
| Shell parsing of YAML/frontmatter is brittle | High | Medium | Keep shell as orchestration only; use `uv run --no-project python` for structured parsing |
| Archive hook introduces duplicate entries on retries | Medium | Medium | Stable dedupe key + integration test for reruns |
| Archive hook delays or fails archive flow | Low | High | Best-effort hook, timeout-conscious implementation, preserve archive exit status |
| Missing `flock` or CLI portability issues | Medium | Medium | Check availability during tests; degrade clearly or document Linux-only assumption in ADR |
| Malformed JSONL/YAML breaks session-start or query path | Medium | High | Tolerant readers, skip bad rows, never make startup fatal |
| Compaction hook and migration overlap, causing duplicates | Medium | Medium | Single dedupe strategy shared across capture/migration/compaction paths |
| Career learnings contain client-specific or sensitive content | Medium | High | Manual curation + legal scan before commit |
| Nightly or startup flows rebuild/read while writes are happening | Low | Medium | Lock writes, atomic replacements for rebuilt files |
| Index grows stale if not rebuilt after writes | Medium | Low | Rebuild explicitly after migration and document whether query reads raw stores or index |

## Out of Scope

- Vector embeddings, semantic search, or RAG infrastructure
- Cross-machine synchronization of the knowledge base
- Backfilling all archived WRKs from full git history
- Automatic extraction of career learnings from historical session logs
- Broad redesign of `MEMORY.md` beyond removing archived WRK summaries and preserving pointer-style usage
- New quota-dependent external services; this design remains local-first

## Standards References

- `.claude/rules/coding-style.md` — shellcheck clean, naming/style constraints
- `.claude/rules/testing.md` — TDD mandatory, tests required before implementation close
- `.claude/rules/legal-compliance.md` — legal scan on committed knowledge content
- `.claude/rules/patterns.md` — prefer scripts/automation over manual LLM-only logic
- `.claude/docs/orchestrator-pattern.md` — archive/session flow integration expectations
- `.claude/rules/python-runtime.md` — all Python execution must use `uv run --no-project python ...`

## Plan Review Confirmation

confirmed_by: <!-- reviewer name, e.g. "vamsee" -->
confirmed_at: <!-- ISO-8601 timestamp -->
decision: changes-requested
notes: >
  Refined for idempotency, malformed-input handling, deterministic rebuilds,
  non-fatal integrations, and explicit Python runtime compliance.

## Codex Notes

1. The draft assumes the orchestrator is the sole source of archived WRK summaries in `MEMORY.md`. That needs proof. Session-end/save/compaction paths are equally plausible and should be audited before changing archive flow.
2. `build-knowledge-index.sh` should prefer full deterministic rebuild, not incremental update. Incremental index mutation adds unnecessary correctness risk.
3. The draft under-specifies idempotency. Both archive capture and migration can easily create duplicates unless a stable dedupe key is defined early.
4. Shell-only parsing of frontmatter, YAML, and JSONL is brittle. If Python is used anywhere for parsing or normalization, it must be invoked as `uv run --no-project python ...`; the draft did not enforce this strongly enough.
5. `archive-item.sh` hook placement needs care. If it runs before the canonical archived file exists, it may read transient state; if it runs after move, it must know the new path. This should be chosen intentionally and tested.
6. `compact-memory.py` should not be changed by default. That is a broader integration surface. Only touch it if diagnosis proves compaction remains a data-loss vector after archive capture and migration exist.
7. AC coverage was thin for malformed rows, duplicate reruns, and concurrent writes. Those are the most likely real-world failure modes for JSONL append workflows.
8. Session-start and resource-intelligence need graceful degradation rules. Missing store files, malformed entries, or query-tool failure must not break startup or mining flows.
9. The draft mentions nightly index rebuild as mitigation but never specifies where that cron integration lives. Since no cron work is in scope, the safer plan is explicit rebuild on writes/migration plus deterministic on-demand rebuild capability.
10. Migration parsing was too optimistic. `MEMORY.md` lines may not have enough structured data to recreate rich entries. The plan should allow partial migrated entries and skip ambiguous lines rather than invent data.
tokens used
41,556
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
version: "1.1-codex"
---

## Mission

Design and implement a structured, durable knowledge persistence system that routes WRK completion learnings out of `MEMORY.md` into a queryable knowledge base, integrates that knowledge into archive flow, resource-intelligence Stage 2, and session-start, and seeds reusable career/domain expertise so session learnings survive compaction and are practically discoverable.

## What

1. **Diagnosis document** — trace the actual write path that causes `WRK-NNN ARCHIVED` summaries to land in `MEMORY.md`, including whether the source is orchestrator behavior, session-exit behavior, or memory compaction side effects.
2. **Architecture ADR** — define a routing table for each knowledge type, storage format, ownership, read paths, and failure behavior.
3. **`scripts/knowledge/`** — implement:
   - `capture-wrk-summary.sh`
   - `query-knowledge.sh`
   - `build-knowledge-index.sh`
   - `migrate-memory-to-knowledge.sh`
4. **`knowledge-base/`** — persistent store:
   - `wrk-completions.jsonl`
   - `career-learnings.yaml`
   - `index.jsonl`
5. **Integration hooks** — archive capture in `scripts/work-queue/archive-item.sh`; knowledge lookup in resource-intelligence and session-start; compaction-safe handling for done-WRK entries.
6. **Migration path** — move only parseable archived WRK summary lines from `MEMORY.md` into the knowledge base with dry-run and idempotency.
7. **`MEMORY.md` slimmed** — keep it as a short working-memory artifact with pointers only; no archived WRK summaries after migration.
8. **Career learnings seed** — initial engineering/finance/software entries in `career-learnings.yaml`, curated and legal-scanned before commit.
9. **TDD coverage** — tests for parsing, duplicate capture, malformed data, empty stores, concurrent writes, and migration safety.
10. **Operational safeguards** — UTC timestamps, atomic writes, `flock` locking, graceful degradation when tools/files are missing, and `uv run --no-project python` for every Python invocation.

## Why

The core failure mode is not just that `MEMORY.md` is large; it is that archived WRK learnings are being stored in a lossy short-term medium with no durable handoff. Once compaction or manual cleanup removes them, the information becomes undiscoverable. That creates repeated re-learning cost, especially in engineering and workflow domains where patterns should compound over time.

The fix needs to be operationally safe. Archive flow cannot block, session-start cannot fail when the knowledge base is absent or malformed, compaction cannot silently drop data, and migration must be repeatable without duplicating entries. The solution therefore needs explicit routing rules, durable storage, idempotent capture, and tests around malformed input and integration boundaries.

## Acceptance Criteria

- [ ] AC-1: Diagnosis document at `assets/WRK-1105/diagnosis.md` identifies the exact write path(s), triggers, and why archived WRK summaries currently persist in `MEMORY.md`
- [ ] AC-2: ADR at `assets/WRK-1105/knowledge-routing-adr.md` defines routing table, schemas, ownership, read/write points, and failure semantics
- [ ] AC-3: `scripts/knowledge/capture-wrk-summary.sh` appends a deduplicated JSONL entry to `knowledge-base/wrk-completions.jsonl` as a best-effort, non-blocking hook
- [ ] AC-4: `scripts/knowledge/query-knowledge.sh` supports `--query`, `--domain`, and `--limit`, degrades cleanly on missing/empty stores, and returns markdown output
- [ ] AC-5: `scripts/knowledge/build-knowledge-index.sh` rebuilds `knowledge-base/index.jsonl` deterministically from all source stores
- [ ] AC-6: `scripts/work-queue/archive-item.sh` invokes capture after gate pass, never blocks archive completion if capture fails, and logs failures clearly
- [ ] AC-7: `.claude/skills/workspace-hub/resource-intelligence/SKILL.md` is updated to include a knowledge-base query step in Stage 2 mining
- [ ] AC-8: `.claude/skills/workspace-hub/session-start/SKILL.md` is updated to surface relevant prior knowledge during startup, with graceful fallback when knowledge data is missing
- [ ] AC-9: `MEMORY.md` contains no archived WRK summary entries after migration and remains at or below 150 lines
- [ ] AC-10: `knowledge-base/career-learnings.yaml` contains at least 10 vetted engineering/finance/software entries with stable schema
- [ ] AC-11: At least 8 tests pass under `scripts/knowledge/tests/`, including malformed input, duplicate capture, and migration dry-run cases
- [ ] AC-12: All Python execution in scripts/tests uses `uv run --no-project python ...`; no bare `python3` is introduced
- [ ] AC-13: Repository checks pass, including shell validation and any applicable Python checks for touched Python files
- [ ] AC-14: Legal scan passes on committed knowledge content, especially `career-learnings.yaml`
- [ ] AC-15: Capture and migration logic are idempotent: rerunning them does not create duplicate knowledge entries for the same source event

## Phases

### Phase 1 — Diagnosis & Architecture

**Objective:** Confirm the real write path for archived WRK summaries and define a robust storage/routing design before implementation.

**Tasks:**
- 1.1 Audit all call sites that can write or reshape `MEMORY.md`, including session orchestration, session-end/save flows, memory compaction, and any helper scripts
- 1.2 Confirm whether archived WRK entries are inserted at creation time, preserved by compaction, or recreated from another source
- 1.3 Inspect `scripts/memory/compact-memory.py` and any callers to determine how done-WRK entries are currently treated and whether preservation hooks already exist
- 1.4 Write `assets/WRK-1105/diagnosis.md` with concrete file/function references, trigger sequence, and evidence for the current behavior
- 1.5 Write `assets/WRK-1105/knowledge-routing-adr.md` defining:
  - knowledge categories
  - destination store per category
  - write-time vs rebuild-time ownership
  - schema/versioning
  - failure handling
  - retention and rebuild strategy
- 1.6 Define stable schemas for:
  - `wrk-completions.jsonl`
  - `career-learnings.yaml`
  - `index.jsonl`
- 1.7 Decide dedupe key strategy up front, preferably a stable `source_id` or `(wrk_id, archived_event_hash)` rather than title text

**Deliverables:**
- `assets/WRK-1105/diagnosis.md`
- `assets/WRK-1105/knowledge-routing-adr.md`
- Schemas embedded in ADR

**Exit Criteria:**
- The write path for archived WRK summaries is evidenced, not inferred
- ADR includes read/write ownership and idempotency rules
- Schema includes required/optional fields and malformed-input policy

---

### Phase 2 — Core Knowledge Scripts (TDD)

**Objective:** Implement core capture/query/index behavior with tests first and minimal parsing fragility.

**Tasks:**
- 2.1 Create failing tests for `capture-wrk-summary.sh`:
  - happy path
  - nonexistent WRK
  - missing `knowledge-base/`
  - malformed frontmatter or missing sections
  - duplicate capture attempt
  - concurrent append behavior
- 2.2 Implement `scripts/knowledge/capture-wrk-summary.sh`
  - shell wrapper preferred
  - if JSON/YAML parsing is needed, call `uv run --no-project python ...`
  - use `flock` and atomic append semantics
  - emit UTC ISO-8601 timestamps
  - exit `0` on operational failure after logging
- 2.3 Create failing tests for `query-knowledge.sh`:
  - keyword match
  - domain filter
  - limit handling
  - empty result
  - missing store files
  - malformed JSONL row tolerance
- 2.4 Implement `scripts/knowledge/query-knowledge.sh`
  - deterministic sort
  - tolerant reads
  - markdown output
  - exit `0` on empty/no-match cases
- 2.5 Create failing tests for `build-knowledge-index.sh`:
  - initial build
  - rebuild determinism
  - malformed source row skipped with warning
  - empty stores
- 2.6 Implement `scripts/knowledge/build-knowledge-index.sh`
  - prefer full rebuild over incremental mutation unless a measured need emerges
  - generate deterministic `index.jsonl`
- 2.7 Create `knowledge-base/` directory with `.gitkeep`
- 2.8 Update ignore rules so runtime JSONL artifacts are handled intentionally without hiding committed seed files such as `career-learnings.yaml`

**Deliverables:**
- `scripts/knowledge/capture-wrk-summary.sh`
- `scripts/knowledge/query-knowledge.sh`
- `scripts/knowledge/build-knowledge-index.sh`
- `scripts/knowledge/tests/`
- `knowledge-base/.gitkeep`

**Exit Criteria:**
- At least 6 script-level tests pass before integration work begins
- Scripts are shellcheck-clean
- No Python execution path uses bare `python3`

---

### Phase 3 — Integration

**Objective:** Wire knowledge capture into archive flow and knowledge surfacing into startup/research flows without introducing blocking failures.

**Tasks:**
- 3.1 Add a best-effort hook to `scripts/work-queue/archive-item.sh` after gate pass succeeds and before final archive move if source data must still be accessible; otherwise after move if archived file is the canonical source
- 3.2 Ensure archive integration logs failures but never changes archive exit status
- 3.3 Add an integration test covering archive flow creating a knowledge entry once, not multiple times on retry
- 3.4 Update `.claude/skills/workspace-hub/resource-intelligence/SKILL.md` to include knowledge-base lookup in Stage 2 mining, with fallback behavior if query tooling/store is unavailable
- 3.5 Update `.claude/skills/workspace-hub/session-start/SKILL.md` to surface relevant prior knowledge for current/top WRK items without making startup dependent on the knowledge store
- 3.6 Reassess `scripts/memory/compact-memory.py` change scope:
  - prefer a narrow preservation hook only if diagnosis proves compaction is a remaining loss vector
  - avoid coupling compaction to new store writes unless necessary
- 3.7 If `compact-memory.py` must be changed, add tests covering malformed lines, duplicate prevention, and no-op behavior when nothing is migratable
- 3.8 Complete cross-review for significant workflow/skill changes before closing implementation

**Deliverables:**
- Updated `scripts/work-queue/archive-item.sh`
- Updated `.claude/skills/workspace-hub/resource-intelligence/SKILL.md`
- Updated `.claude/skills/workspace-hub/session-start/SKILL.md`
- Updated `scripts/memory/compact-memory.py` only if required by diagnosis

**Exit Criteria:**
- Archive integration test passes
- Session-start/resource-intelligence behavior is explicitly non-fatal on missing or malformed knowledge data
- Cross-review verdict is `APPROVE` or `MINOR`

---

### Phase 4 — Migration & Career Learnings

**Objective:** Migrate durable archived knowledge out of `MEMORY.md`, seed reusable expertise, and verify the working-memory artifact stays lean.

**Tasks:**
- 4.1 Write failing tests for `migrate-memory-to-knowledge.sh`:
  - dry-run
  - real migration
  - malformed archived summary lines
  - duplicate migration rerun
  - atomic rewrite of `MEMORY.md`
- 4.2 Implement `scripts/knowledge/migrate-memory-to-knowledge.sh`
  - parse only recognized archived summary formats
  - skip ambiguous lines with warnings
  - use temp file + atomic move for `MEMORY.md`
  - use same dedupe strategy as capture
  - use `uv run --no-project python ...` for structured parsing if needed
- 4.3 Run migration in dry-run mode and inspect proposed counts
- 4.4 Run migration for real and verify `MEMORY.md` contains pointers only and remains within size target
- 4.5 Seed `knowledge-base/career-learnings.yaml` with at least 10 entries spanning engineering, finance, and software
- 4.6 Validate career-learning schema and run legal scan before commit
- 4.7 Run memory quality evaluation and confirm archived WRK noise is removed from working memory
- 4.8 Rebuild `knowledge-base/index.jsonl` after migration and seed creation

**Deliverables:**
- `scripts/knowledge/migrate-memory-to-knowledge.sh`
- Updated `MEMORY.md`
- `knowledge-base/career-learnings.yaml`
- Rebuilt `knowledge-base/index.jsonl`

**Exit Criteria:**
- `MEMORY.md` line count is `<= 150`
- Archived WRK summary lines are removed from `MEMORY.md`
- Migration is idempotent on rerun
- Legal scan passes on new committed knowledge content

---

## Pseudocode

### capture-wrk-summary.sh
```text
function capture_wrk_summary(wrk_id) -> exit 0
  resolve canonical wrk_file from pending/archive paths
  if wrk_file missing:
    warn and exit 0

  parse frontmatter + selected sections from wrk_file
  if required fields missing:
    warn, build partial entry if safe, else exit 0

  source_id = stable capture key derived from wrk_id + archive state
  archived_at = current UTC ISO-8601 timestamp

  collect optional enrichments:
    mission
    domain/category
    evidence-derived patterns
    follow_on ids

  mkdir -p knowledge-base or warn and exit 0
  open lock on wrk-completions.jsonl.lock
  if entry with same source_id already exists:
    exit 0

  append one JSON object line atomically to knowledge-base/wrk-completions.jsonl
  exit 0
```

### query-knowledge.sh
```text
function query_knowledge(--query Q, --domain D, --limit N=5) -> markdown stdout
  load records from known stores:
    wrk-completions.jsonl
    career-learnings.yaml
    optional index.jsonl if that is the canonical query source

  tolerate missing files
  skip malformed rows with warning to stderr

  normalize query/domain inputs
  filter by domain if provided
  score by keyword presence across title, mission, tags, patterns, learnings
  sort deterministically by score desc, then recency desc, then id asc
  take top N

  if none:
    print "No knowledge entries found."
    exit 0

  print markdown blocks with stable fields only
  exit 0
```

### build-knowledge-index.sh
```text
function build_knowledge_index() -> exit 0/nonzero on true build failure
  load all source stores
  skip malformed source rows with warning count
  normalize each record into common index schema
  sort deterministically
  write index to temp file
  atomically replace knowledge-base/index.jsonl
  exit 0
```

### migrate-memory-to-knowledge.sh
```text
function migrate_memory_to_knowledge(--dry-run) -> exit 0/nonzero on unsafe rewrite failure
  read MEMORY.md
  classify each line:
    migratable archived summary
    ambiguous archived-like line
    keep

  for migratable lines:
    derive stable source_id
    build entry payload tagged source="memory-migration"

  if dry-run:
    print counts: migrate / skip ambiguous / keep / duplicates
    exit 0

  append only non-duplicate entries to wrk-completions.jsonl under lock
  write kept lines back to MEMORY.md via temp file + mv
  rebuild index
  print summary counts
  exit 0
```

## Tests / Evals

| Test | Type | Expected |
|------|------|----------|
| `test_capture_happy_path` | happy | Appends one valid WRK completion entry with expected required fields |
| `test_capture_nonexistent_wrk` | edge | Exits `0`, logs warning, performs no write |
| `test_capture_creates_knowledge_dir` | edge | Creates missing `knowledge-base/` and writes entry |
| `test_capture_missing_required_fields` | edge | Handles malformed/missing frontmatter or mission safely without crashing |
| `test_capture_deduplicates_same_wrk_event` | edge | Repeated capture for same source event does not create duplicate rows |
| `test_capture_concurrent_writes` | edge | Parallel capture attempts do not corrupt JSONL |
| `test_query_domain_filter` | happy | `--domain` returns only matching entries |
| `test_query_limit_and_sort` | happy | `--limit` respects deterministic ranking |
| `test_query_empty_result` | edge | Prints clean no-result message, exits `0` |
| `test_query_skips_malformed_rows` | edge | Malformed JSONL rows are skipped with warning, valid rows still return |
| `test_build_index_deterministic_rebuild` | happy | Two rebuilds from same inputs produce identical index |
| `test_build_index_skips_bad_source_rows` | edge | Bad source rows do not fail whole build |
| `test_migrate_dry_run` | happy | Reports counts and does not modify files |
| `test_migrate_reduces_memory_lines` | happy | Real migration removes migratable archived lines from `MEMORY.md` |
| `test_migrate_idempotent_rerun` | edge | Second run creates no duplicates and leaves `MEMORY.md` unchanged |
| `test_archive_hook_best_effort` | integration | Archive completes even if capture hook fails |
| `test_archive_hook_writes_once` | integration | Archive flow creates exactly one knowledge entry for the WRK |

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Assumed write source is wrong; fix targets wrong layer | Medium | High | Phase 1 diagnosis must cite exact call site before implementation |
| Shell parsing of YAML/frontmatter is brittle | High | Medium | Keep shell as orchestration only; use `uv run --no-project python` for structured parsing |
| Archive hook introduces duplicate entries on retries | Medium | Medium | Stable dedupe key + integration test for reruns |
| Archive hook delays or fails archive flow | Low | High | Best-effort hook, timeout-conscious implementation, preserve archive exit status |
| Missing `flock` or CLI portability issues | Medium | Medium | Check availability during tests; degrade clearly or document Linux-only assumption in ADR |
| Malformed JSONL/YAML breaks session-start or query path | Medium | High | Tolerant readers, skip bad rows, never make startup fatal |
| Compaction hook and migration overlap, causing duplicates | Medium | Medium | Single dedupe strategy shared across capture/migration/compaction paths |
| Career learnings contain client-specific or sensitive content | Medium | High | Manual curation + legal scan before commit |
| Nightly or startup flows rebuild/read while writes are happening | Low | Medium | Lock writes, atomic replacements for rebuilt files |
| Index grows stale if not rebuilt after writes | Medium | Low | Rebuild explicitly after migration and document whether query reads raw stores or index |

## Out of Scope

- Vector embeddings, semantic search, or RAG infrastructure
- Cross-machine synchronization of the knowledge base
- Backfilling all archived WRKs from full git history
- Automatic extraction of career learnings from historical session logs
- Broad redesign of `MEMORY.md` beyond removing archived WRK summaries and preserving pointer-style usage
- New quota-dependent external services; this design remains local-first

## Standards References

- `.claude/rules/coding-style.md` — shellcheck clean, naming/style constraints
- `.claude/rules/testing.md` — TDD mandatory, tests required before implementation close
- `.claude/rules/legal-compliance.md` — legal scan on committed knowledge content
- `.claude/rules/patterns.md` — prefer scripts/automation over manual LLM-only logic
- `.claude/docs/orchestrator-pattern.md` — archive/session flow integration expectations
- `.claude/rules/python-runtime.md` — all Python execution must use `uv run --no-project python ...`

## Plan Review Confirmation

confirmed_by: <!-- reviewer name, e.g. "vamsee" -->
confirmed_at: <!-- ISO-8601 timestamp -->
decision: changes-requested
notes: >
  Refined for idempotency, malformed-input handling, deterministic rebuilds,
  non-fatal integrations, and explicit Python runtime compliance.

## Codex Notes

1. The draft assumes the orchestrator is the sole source of archived WRK summaries in `MEMORY.md`. That needs proof. Session-end/save/compaction paths are equally plausible and should be audited before changing archive flow.
2. `build-knowledge-index.sh` should prefer full deterministic rebuild, not incremental update. Incremental index mutation adds unnecessary correctness risk.
3. The draft under-specifies idempotency. Both archive capture and migration can easily create duplicates unless a stable dedupe key is defined early.
4. Shell-only parsing of frontmatter, YAML, and JSONL is brittle. If Python is used anywhere for parsing or normalization, it must be invoked as `uv run --no-project python ...`; the draft did not enforce this strongly enough.
5. `archive-item.sh` hook placement needs care. If it runs before the canonical archived file exists, it may read transient state; if it runs after move, it must know the new path. This should be chosen intentionally and tested.
6. `compact-memory.py` should not be changed by default. That is a broader integration surface. Only touch it if diagnosis proves compaction remains a data-loss vector after archive capture and migration exist.
7. AC coverage was thin for malformed rows, duplicate reruns, and concurrent writes. Those are the most likely real-world failure modes for JSONL append workflows.
8. Session-start and resource-intelligence need graceful degradation rules. Missing store files, malformed entries, or query-tool failure must not break startup or mining flows.
9. The draft mentions nightly index rebuild as mitigation but never specifies where that cron integration lives. Since no cron work is in scope, the safer plan is explicit rebuild on writes/migration plus deterministic on-demand rebuild capability.
10. Migration parsing was too optimistic. `MEMORY.md` lines may not have enough structured data to recreate rich entries. The plan should allow partial migrated entries and skip ambiguous lines rather than invent data.
