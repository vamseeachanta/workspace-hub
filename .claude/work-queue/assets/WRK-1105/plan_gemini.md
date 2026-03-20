YOLO mode is enabled. All tool calls will be automatically approved.
Loaded cached credentials.
YOLO mode is enabled. All tool calls will be automatically approved.
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
version: "1.1"
---

## Mission

Design and implement a highly robust, structured knowledge persistence system that routes WRK completion learnings out of MEMORY.md into a queryable knowledge-base, integrates it with resource-intelligence Stage 2 and session-start, and seeds career domain expertise — so each session builds on what past sessions learned without risking data corruption or workflow blocking.

## What

1. **Diagnosis document** — trace why WRK-NNN ARCHIVED summaries land in MEMORY.md (call-site audit)
2. **Architecture ADR** — knowledge routing table: each knowledge type → correct destination, including fault tolerance and concurrency considerations.
3. **`scripts/knowledge/`** — three core scripts: `capture-wrk-summary.sh`, `query-knowledge.sh`, `build-knowledge-index.sh`
4. **`knowledge-base/`** — persistent store: `wrk-completions.jsonl`, `career-learnings.yaml`, `index.jsonl`
5. **Integration hooks** — archive-item.sh (post-archive capture), resource-intelligence SKILL.md (category 10), session-start SKILL.md (Step 2 enrichment)
6. **Migration script** — `scripts/knowledge/migrate-memory-to-knowledge.sh` — safely moves WRK ARCHIVED summaries from MEMORY.md to knowledge-base
7. **MEMORY.md slimmed** — ≤150 lines, pointers only
8. **Career learnings seed** — initial engineering/finance/software entries in career-learnings.yaml (sourced from engineering-modules.md, legal-scanned before commit)
9. **≥16 TDD tests** in `scripts/knowledge/tests/` to ensure reliability under edge cases, malformed outputs, and concurrency.

## Why

MEMORY.md has grown to 146/200 lines, with ~25 WRK-NNN ARCHIVED entries. These accumulate because the orchestrator writes summaries manually during sessions — no script captures them at archive time. When compact-memory.py hits the line limit, these learnings are evicted and permanently lost. Engineering domain expertise exists nowhere in the system. Each session rediscovers patterns already learned. By implementing a robust, decoupled knowledge base, each session becomes measurably more capable without overloading context windows or risking data loss during race conditions.

## Acceptance Criteria

- [ ] AC-1: Diagnosis document (`assets/WRK-1105/diagnosis.md`) explaining why WRK summaries land in MEMORY.md
- [ ] AC-2: Architecture ADR (`assets/WRK-1105/knowledge-routing-adr.md`) with knowledge routing table and failure mode analysis
- [ ] AC-3: `scripts/knowledge/capture-wrk-summary.sh` — writes JSONL entry to knowledge-base/ at archive time (strictly non-blocking, uses `flock` for concurrency)
- [ ] AC-4: `scripts/knowledge/query-knowledge.sh` — query by keyword/domain, returns markdown output. Gracefully handles malformed JSONL or empty stores.
- [ ] AC-5: `scripts/knowledge/build-knowledge-index.sh` — builds knowledge-base/index.jsonl from all stores, safe for nightly cron execution.
- [ ] AC-6: `archive-item.sh` calls capture-wrk-summary.sh as best-effort hook after gate pass
- [ ] AC-7: resource-intelligence SKILL.md updated with category 10 (knowledge-base query), including fallback logic if knowledge-base is temporarily unavailable
- [ ] AC-8: session-start SKILL.md updated with knowledge surfacing in Step 2, handling partial/fenced LLM extraction outputs gracefully
- [ ] AC-9: MEMORY.md ≤150 lines (pointers only) after migration
- [ ] AC-10: career-learnings.yaml seeded with ≥10 engineering/finance/software entries
- [ ] AC-11: ≥16 TDD tests pass in `scripts/knowledge/tests/` covering parsing failures, lock contention, and corrupt files
- [ ] AC-12: `check-all.sh` passes (ruff + mypy if any Python; shellcheck on bash scripts)
- [ ] AC-13: Legal scan passes on all committed content

## Phases

### Phase 1 — Diagnosis & Architecture

**Objective:** Confirm the exact call-site that writes WRK summaries to MEMORY.md; define the knowledge routing table with reliability engineering principles.

**Tasks:**
- 1.1 Audit session logs, MEMORY.md write patterns, and auto-memory rules to confirm WRK summaries are written by the orchestrator (not scripts)
- 1.2 Read compact-memory.py to confirm it evicts done-WRK entries without preservation
- 1.3 Write `assets/WRK-1105/diagnosis.md` — precise call-site, trigger mechanism, current fate of evicted entries
- 1.4 Write `assets/WRK-1105/knowledge-routing-adr.md` — routing table with rationale for each knowledge type, including concurrency and data corruption mitigations.
- 1.5 Define `knowledge-base/` JSONL schema for wrk-completions.jsonl and career-learnings.yaml

**Deliverables:**
- `assets/WRK-1105/diagnosis.md`
- `assets/WRK-1105/knowledge-routing-adr.md`
- JSONL schema (embedded in ADR)

**Exit Criteria:**
- Diagnosis confirmed: WRK summaries enter MEMORY.md via orchestrator auto-memory, not scripts
- Routing table covers all 6 knowledge types from the WRK item and addresses race conditions

---

### Phase 2 — Core Knowledge Scripts (TDD)

**Objective:** Implement capture, query, and index scripts with test-driven development, ensuring high reliability.

**Tasks:**
- 2.1 Write failing tests for capture-wrk-summary.sh (happy path, non-existent WRK, missing dir, file lock contention, malformed source YAML)
- 2.2 Implement `scripts/knowledge/capture-wrk-summary.sh` to pass tests, enforcing `flock` and safe parsing.
- 2.3 Write failing tests for query-knowledge.sh (keyword match, domain filter, empty result, corrupt JSONL line skipping)
- 2.4 Implement `scripts/knowledge/query-knowledge.sh`
- 2.5 Write failing tests for build-knowledge-index.sh (index creation, incremental update, concurrent run prevention)
- 2.6 Implement `scripts/knowledge/build-knowledge-index.sh`
- 2.7 Create `knowledge-base/` directory with `.gitkeep`; add `knowledge-base/*.jsonl` to `.gitignore` (runtime data)

**Deliverables:**
- `scripts/knowledge/capture-wrk-summary.sh`
- `scripts/knowledge/query-knowledge.sh`
- `scripts/knowledge/build-knowledge-index.sh`
- `scripts/knowledge/tests/` (≥16 tests)
- `knowledge-base/.gitkeep`

**Exit Criteria:**
- ≥16 TDD tests pass covering edge cases and failure modes
- Scripts are shellcheck-clean and handle malformed data inputs

---

### Phase 3 — Integration

**Objective:** Wire knowledge capture into archive flow; enrich resource-intelligence and session-start reliably.

**Tasks:**
- 3.1 Add strictly non-blocking capture hook to `scripts/work-queue/archive-item.sh` (after gate pass, before archive move, routing stderr to log)
- 3.2 Update `.claude/skills/workspace-hub/resource-intelligence/SKILL.md` — add category 10 (knowledge-base query), ensuring graceful degradation if parsing LLM output fails.
- 3.3 Update `.claude/skills/workspace-hub/session-start/SKILL.md` — add Step 2b: query knowledge-base for relevant entries matching today's WRK items
- 3.4 Update `scripts/memory/compact-memory.py` — route done-WRK entries to knowledge-base/ before evicting them (AC-9 enabler)
- 3.5 Codex cross-review of skill changes (resource-intelligence, session-start)

**Deliverables:**
- Updated `archive-item.sh`
- Updated `resource-intelligence/SKILL.md`
- Updated `session-start/SKILL.md`
- Updated `compact-memory.py`

**Exit Criteria:**
- archive-item.sh integration test: archiving a WRK creates a knowledge-base entry without blocking or failing the archive if the write fails
- resource-intelligence SKILL.md Codex-reviewed APPROVE or MINOR
- session-start SKILL.md Codex-reviewed APPROVE or MINOR

---

### Phase 4 — Migration & Career Learnings

**Objective:** Slim MEMORY.md and seed career domain expertise safely.

**Tasks:**
- 4.1 Write `scripts/knowledge/migrate-memory-to-knowledge.sh` — safely identifies WRK-NNN ARCHIVED lines in MEMORY.md, converts to JSONL entries, removes from MEMORY.md
- 4.2 Run migration in dry-run mode, verify output and atomicity
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
function capture_wrk_summary(wrk_id) → exit 0 (strictly best-effort, non-blocking)
  # Wrap entirely in a try/catch equivalent to prevent archive hook failure
  wrk_file = pending/ or archive/ WRK-NNN.md
  if wrk_file not found: log warning, exit 0
  
  title = parse frontmatter title from wrk_file
  category = parse frontmatter category/subcategory from wrk_file
  archived_at = current ISO 8601 timestamp
  mission = extract ## Mission section body from wrk_file
  
  patterns = []
  if evidence/resource-intelligence.yaml exists and is valid YAML:
    patterns = top_p2_gaps + constraints from yaml
  
  follow_ons = []
  if evidence/future-work.yaml exists and is valid YAML:
    follow_ons = recommendations[].id list
    
  ensure knowledge-base/ dir exists (mkdir -p, exit 0 on failure)
  
  entry = {"id": wrk_id, "title": title, "category": category,
           "archived_at": archived_at, "mission": mission,
           "patterns": patterns, "follow_ons": follow_ons}
           
  # Use flock for atomicity with a short timeout to prevent hanging
  (
    flock -w 2 200 || exit 0
    append JSON line to knowledge-base/wrk-completions.jsonl
  ) 200>knowledge-base/.wrk-completions.lock
  
  exit 0
```

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| career-learnings.yaml contains client identifiers | Medium | High | Legal scan mandatory before commit (AC-13) |
| archive-item.sh hook stalls archive gate on failure | Low | High | Best-effort hook: redirect stderr to log, always exit 0, use short timeout locks |
| compact-memory.py routing change drops valid entries | Medium | Medium | Dry-run test before applying; TDD test covers migration path |
| SKILL.md updates require Codex gate | High | Low | Plan for it; Codex fallback to Claude Opus per quota policy |
| JSONL parsing fails due to malformed data | Medium | Medium | Implement robust parsing using `jq` with fallback skip-logic |
| Nightly index script overlaps/hangs | Low | High | Use exclusive locks (`flock`) for the cron script to prevent concurrent runs |

## Out of Scope

- Vector embeddings or semantic search (not yet needed; JSONL with keyword search is sufficient for Phase 1)
- Cross-machine knowledge sync (dev-secondary, licensed-win-1) — knowledge-base/ lives on dev-primary only
- Automated career learnings extraction from engineering session logs (manual seed only in this WRK)
- Retroactive backfill of all archived WRK items from git history (migrate MEMORY.md entries only)

## Standards References

- `.claude/rules/coding-style.md` — shellcheck clean, snake_case, 400L file limit
- `.claude/rules/testing.md` — TDD mandatory, ≥16 tests
- `.claude/rules/legal-compliance.md` — legal scan on career-learnings.yaml
- `.claude/rules/git-workflow.md` — feature/ branch, conventional commits
- `.claude/rules/patterns.md` — scripts over LLM judgment; no god objects
- `.claude/docs/orchestrator-pattern.md` — delegation, checkpoint/resume

## Plan Review Confirmation

confirmed_by: <!-- reviewer name, e.g. "vamsee" -->
confirmed_at: <!-- ISO-8601 timestamp -->
decision: <!-- passed | changes-requested -->
notes: <!-- optional -->

---

# Gemini Notes

As a systems reliability agent, I have reviewed the draft and identified several critical areas that require strengthening. The refined plan above incorporates these adjustments, specifically expanding the test suite to ≥16 tests and solidifying the operational scripts against potential failures.

### 1. Failure modes in LLM output parsing
When `resource-intelligence` or `session-start` skills rely on Gemini/Claude to extract or format knowledge from the JSONL stores, the output may occasionally arrive as partial YAML, fenced code blocks (e.g., ```json ... ```), or conversational prose. 
**Mitigation added:** The SKILL.md updates (AC-7, AC-8) must now explicitly instruct the LLM to provide raw, cleanly formatted data or include robust parser logic (via `jq` or `yq`) in the consumption scripts that strips markdown fences and ignores conversational wrappers.

### 2. Carry-forward logic & malformed evidence files
Scripts parsing `evidence/resource-intelligence.yaml` and `evidence/future-work.yaml` (or equivalent signal files) must anticipate missing, empty, or structurally corrupt files. If `archive-item.sh` blindly tries to parse a malformed YAML file via `yq`, the script will throw an error, potentially breaking the archive flow.
**Mitigation added:** The pseudocode for `capture-wrk-summary.sh` now explicitly guards YAML parsing. It verifies existence and validity before extracting `patterns` or `follow_ons`, defaulting to empty arrays without failing.

### 3. Dual-mode tie-break (Engineering vs. Harness)
When querying the knowledge base, deciding whether to prioritize engineering domain expertise or orchestrator/harness patterns can be ambiguous. The original draft did not specify how conflicting or equally scored results are ranked.
**Observation:** If a query matches both domain logic (e.g., FEA/CFD) and harness mechanics, tie-breaking logic is necessary. While not explicitly codified in the draft's CLI tool, the design should ensure that `query-knowledge.sh` applies a stable sort, potentially weighting `engineering` category learnings higher than `harness` if the session context demands it, or simply sorting by `archived_at` descending as a predictable fallback.

### 4. Test coverage (Scaling to ≥16 Tests)
The original proposal of 5 tests is insufficient for the surface area of this architecture. Persistence layers are highly prone to edge-case failures.
**Mitigation added:** AC-11 has been updated to require ≥16 TDD tests. The expanded suite must cover:
*   File locking contention (`flock` timeouts).
*   Malformed source YAML gracefully failing to empty arrays.
*   Corrupt JSONL lines being skipped by `query-knowledge.sh` without crashing the entire query.
*   Empty query results and missing directory edge cases.
*   Atomicity of `migrate-memory-to-knowledge.sh` (e.g., what happens if it crashes mid-write?).

### 5. Nightly Cron Risks
If `build-knowledge-index.sh` is scheduled as a nightly cron job, several reliability risks emerge:
*   **API Quota/Drift:** If the indexing process ever relies on Gemini/Claude to summarize, a 3 AM quota limit or a CLI version drift could silently fail the cron job.
*   **File Lock Races:** If a late-night session archives a WRK exactly when the cron job runs, `wrk-completions.jsonl` might be locked or truncated.
**Mitigation added:** The refined plan emphasizes robust concurrency controls. AC-5 and the Risks section now mandate exclusive file locks (`flock`) for the indexing script to prevent concurrent runs or read-during-write corruption. Indexing should currently remain a pure bash/jq operation to avoid API dependency risks entirely.
