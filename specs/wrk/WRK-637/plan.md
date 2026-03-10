# WRK-637 Plan Draft — Memory Governance: Compaction, Tiering, Eviction

**Route:** B (Medium) | **Computer:** ace-linux-1 | **Drafted:** 2026-03-09

---

## Mission

Build `scripts/memory/compact-memory.py` (and `curate-memory.py`) to enforce the memory
tier model, evict stale bullets, and integrate with comprehensive-learning Phase 3b/3c —
preventing context-rot in MEMORY.md and topic files.

---

## Plan

### Phase 1 — TDD Setup (tests first)

1. Create `tests/memory/` directory with `conftest.py` and fixtures
2. Write `tests/memory/test_compact_memory.py` covering:
   - `--dry-run` runs cleanly, outputs audit report, writes no files
   - Done-WRK eviction: bullet referencing closed WRK item moved to `archive/done-wrk.md`
   - Path staleness: bullet with non-existent path flagged to `archive/stale-paths.md`
   - `# keep` marker exempts bullet from age eviction
   - Compaction frees ≥10 lines from engineering-modules.md (currently 173L, over 150L limit)
   - Idempotency: second run on already-compacted file → zero evictions
   - `compact-log.jsonl` written with required fields (timestamp, lines_freed_memory, lines_freed_topics)
3. Write `tests/memory/test_curate_memory.py` covering:
   - Bullet classification (memory-keep / domain-doc / skill-update / archive)
   - Promotion candidate file written correctly
4. All tests RED before implementation begins

### Phase 2 — `compact-memory.py` implementation

File: `scripts/memory/compact-memory.py`

**Phase A — audit:**
- Resolve memory dir: `~/.claude/projects/*/memory/` (glob, pick active project)
- Parse MEMORY.md and all topic files (`*.md`, skip `archive/`)
- Apply eviction rules in order:
  1. Done-WRK expiry: grep bullet for `WRK-NNN`; check work-queue status; >30 days done → evict
  2. Path staleness: extract file paths from bullet; `os.path.exists()` check → flag
  3. Command staleness: spot-check 3 commands/run via `subprocess.run(timeout=5)` → flag
  4. Dedup: 80% overlap (token set ratio) between bullets in same file → keep fresher
  5. Age eviction: no session signal reference for 90+ days AND no `# keep` → evict
- Write `memory/compact-audit.md` (proposed actions, no mutations yet)

**Phase B — `--dry-run`:**
- Print audit to stdout; exit 0

**Phase C — apply:**
- Create `archive/` dir if missing
- Move evicted bullets to `archive/<category>.md`
- Rewrite topic files without evicted bullets
- Update MEMORY.md section pointers if topic files changed
- Append to `memory/compact-log.jsonl`: `{timestamp, lines_freed_memory, lines_freed_topics, bullets_evicted, bullets_archived}`

**Trigger check** (at script entry):
- MEMORY.md > 180L → run compaction
- Any topic file > 150L → run compaction
- `--force` flag bypasses trigger check

### Phase 3 — `curate-memory.py` implementation

File: `scripts/memory/curate-memory.py`

- Classify each bullet: `memory-keep | domain-doc | skill-update | archive`
- Write promotion candidates to `.claude/state/candidates/memory-promotion-candidates.md`
- Used by Phase 3c of comprehensive-learning (non-mandatory, log failure and continue)

### Phase 4 — Integration

- Verify comprehensive-learning SKILL.md Phase 3b entry is correct (script path matches)
- Verify pipeline-detail.md Phase 3b/3c entries reference correct script paths
- Update WRK-637.md frontmatter: `html_output_ref`, `plan_html_review_draft_ref`, `plan_html_review_final_ref`

---

## Test Strategy

| Test | Expected | Gate |
|------|----------|------|
| `--dry-run` on current memory files | audit report, no writes | PASS |
| Done-WRK eviction | WRK refs with status:done >30d moved to archive | PASS |
| Path staleness | ≥1 stale path flagged (current files have some) | PASS |
| Frees ≥10 lines | engineering-modules.md 173L → ≤150L | PASS |
| `# keep` exemption | kept bullets survive eviction pass | PASS |
| Idempotency | second run → 0 evictions | PASS |
| compact-log.jsonl | file exists, JSON valid, required fields present | PASS |

Minimum 3 PASS before Stage 10 closes.

---

## Acceptance Criteria Map

| AC | Phase | Test |
|----|-------|------|
| dry-run works | 2 | test_compact_memory::test_dry_run |
| done-WRK eviction | 2 | test_compact_memory::test_done_wrk_eviction |
| path staleness | 2 | test_compact_memory::test_path_staleness |
| ≥10 lines freed | 2 | test_compact_memory::test_lines_freed |
| MEMORY.md ≤180L after WRK-635 bulk scan | 2+4 | integration |
| `# keep` exemption | 2 | test_compact_memory::test_keep_exemption |
| comp-learning Phase 3b updated | 4 | manual verify |
| compact-log.jsonl | 2 | test_compact_memory::test_log_written |
| scan-sessions.py headroom check | 4 | WRK-635 integration (deferred) |

---

## Out of Scope

- WRK-635 `scan-sessions.py` implementation (separate WRK)
- Memory file content decisions (what to keep/evict) — only the governance mechanism
- curate-memory.py full Phase 3c integration (script only; cron wiring deferred)
- Memory quality eval harness (% stale, % verified, signal density, usage tracking) → spin off as WRK-638
