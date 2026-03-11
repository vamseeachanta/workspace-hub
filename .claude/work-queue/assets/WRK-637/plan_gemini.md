YOLO mode is enabled. All tool calls will be automatically approved.
Loaded cached credentials.
YOLO mode is enabled. All tool calls will be automatically approved.
# WRK-637 Plan Draft — Memory Governance: Compaction, Tiering, Eviction (Refined)

**Route:** B (Medium) | **Computer:** ace-linux-1 | **Drafted:** 2026-03-09

---

## Mission

Build `scripts/memory/compact-memory.py` and `curate-memory.py` to enforce the memory tier model, evict stale bullets, and integrate with comprehensive-learning Phase 3b/3c. The implementation must prioritize **robustness, atomic operations, and fail-safe degradation** to prevent context-rot in `MEMORY.md` and topic files without risking accidental data loss or pipeline crashes during automated cron execution.

---

## Plan

### Phase 1 — TDD Setup (tests first)

1. Create `tests/memory/` directory with `conftest.py` and fixtures. Include fixtures for malformed files, locked files, and mock LLM responses.
2. Write `tests/memory/test_compact_memory.py` covering:
   - `--dry-run` runs cleanly, outputs audit report, writes no files.
   - Done-WRK eviction: bullet referencing closed WRK item moved to `archive/done-wrk.md`.
   - Path staleness: bullet with non-existent path flagged to `archive/stale-paths.md`.
   - Command staleness: handles timeouts gracefully (e.g., `subprocess.run` hangs) without crashing.
   - `# keep` marker exempts bullet from age eviction (test variations like `#keep`, `<!-- keep -->`).
   - Compaction frees ≥10 lines from `engineering-modules.md` (currently 173L, over 150L limit).
   - Idempotency: second run on already-compacted file → zero evictions.
   - File state preservation: missing, empty, or corrupt files (e.g., `compact-log.jsonl`) are handled cleanly and re-initialized.
   - Atomic writes: interruption during write does not corrupt `MEMORY.md`.
3. Write `tests/memory/test_curate_memory.py` covering:
   - Bullet classification (`memory-keep | domain-doc | skill-update | archive`).
   - LLM Output parsing failures: handles partial YAML, markdown fences, conversational filler, or empty responses gracefully.
   - Promotion candidate file written correctly and atomically.
4. All 16+ tests RED before implementation begins.

### Phase 2 — `compact-memory.py` implementation

File: `scripts/memory/compact-memory.py`

**Phase A — audit:**
- Resolve memory dir: `~/.claude/projects/*/memory/` (glob, pick active project). Handle cases where 0 or >1 directories are found.
- Parse `MEMORY.md` and all topic files (`*.md`, skip `archive/`).
- Apply eviction rules in order:
  1. Done-WRK expiry: grep bullet for `WRK-NNN`; check work-queue status; >30 days done → evict.
  2. Path staleness: extract file paths from bullet; `os.path.exists()` check → flag.
  3. Command staleness: spot-check 3 commands/run via `subprocess.run(timeout=5)`. **Must catch `TimeoutExpired` and treat as stale/flagged without crashing.**
  4. Dedup: 80% overlap (token set ratio) between bullets in same file → keep fresher. *(Note: fallback to semantic similarity if token ratio is ambiguous).*
  5. Age eviction: no session signal reference for 90+ days AND no `# keep` → evict.
- Write `memory/compact-audit.md` (proposed actions, no mutations yet).

**Phase B — `--dry-run`:**
- Print audit to stdout; exit 0.

**Phase C — apply:**
- **Acquire File Lock:** Implement a `.lock` mechanism to prevent race conditions if an agent is concurrently updating memory.
- Create `archive/` dir if missing.
- Move evicted bullets to `archive/<category>.md` (append mode).
- Rewrite topic files without evicted bullets using **atomic renames** (write to `.tmp`, then `mv`).
- Update `MEMORY.md` section pointers if topic files changed (atomic write).
- Append to `memory/compact-log.jsonl`: `{timestamp, lines_freed_memory, lines_freed_topics, bullets_evicted, bullets_archived}`. If log is corrupt, backup and start fresh.
- **Release File Lock.**

**Trigger check** (at script entry):
- `MEMORY.md` > 180L → run compaction.
- Any topic file > 150L → run compaction.
- `--force` flag bypasses trigger check.

### Phase 3 — `curate-memory.py` implementation

File: `scripts/memory/curate-memory.py`

- Use Gemini CLI (L3 parsing) to classify each bullet: `memory-keep | domain-doc | skill-update | archive`.
- **Parsing Robustness:** Extract classification using strict regex from the LLM output. Strip markdown code fences (e.g., ```yaml). If the output is prose or unrecognizable, default to `memory-keep` to prevent accidental deletion and log an error.
- Write promotion candidates to `.claude/state/candidates/memory-promotion-candidates.md` atomically.
- Used by Phase 3c of comprehensive-learning. If API quota is hit or CLI drifts, log failure and exit 0 to allow the pipeline to continue.

### Phase 4 — Integration

- Verify comprehensive-learning `SKILL.md` Phase 3b entry is correct (script path matches).
- Verify `pipeline-detail.md` Phase 3b/3c entries reference correct script paths.
- Update `WRK-637.md` frontmatter: `html_output_ref`, `plan_html_review_draft_ref`, `plan_html_review_final_ref`.

---

## Test Strategy

To ensure sufficient AC surface area coverage, the test suite is expanded to 16 test cases focusing on failure modes.

| Test | Expected | Gate |
|------|----------|------|
| `--dry-run` on current memory files | audit report, no writes | PASS |
| Done-WRK eviction | WRK refs with status:done >30d moved to archive | PASS |
| Path staleness | ≥1 stale path flagged | PASS |
| Command staleness timeout | Command hanging >5s is caught, script continues | PASS |
| Dedup thresholding | 80% token overlap successfully identifies duplicate | PASS |
| Frees ≥10 lines | `engineering-modules.md` 173L → ≤150L | PASS |
| `# keep` exemption | kept bullets survive eviction pass (various formats) | PASS |
| Idempotency | second run → 0 evictions | PASS |
| `compact-log.jsonl` missing | File is created with valid JSON | PASS |
| `compact-log.jsonl` corrupt | Corrupt file backed up, new file created | PASS |
| Atomic File Writes | Write interruption preserves original `MEMORY.md` | PASS |
| File Lock Prevention | Concurrent run aborts if `.lock` exists | PASS |
| L3 Parse: Clean YAML | Successfully extracts classification | PASS |
| L3 Parse: Fenced Code | Successfully strips markdown fences | PASS |
| L3 Parse: Prose/Conversational | Regresses safely to `memory-keep` default | PASS |
| Missing `portfolio-signals.yaml` | Carry-forward logic handles missing external state files gracefully | PASS |

---

## Acceptance Criteria Map

| AC | Phase | Test |
|----|-------|------|
| dry-run works | 2 | `test_dry_run` |
| done-WRK eviction | 2 | `test_done_wrk_eviction` |
| path staleness | 2 | `test_path_staleness` |
| ≥10 lines freed | 2 | `test_lines_freed` |
| MEMORY.md ≤180L | 2+4 | integration |
| `# keep` exemption | 2 | `test_keep_exemption` |
| L3 output robustness | 3 | `test_l3_parse_*` |
| atomic operations | 2+3 | `test_atomic_writes`, `test_file_lock` |
| comp-learning Phase 3b | 4 | manual verify |
| compact-log.jsonl | 2 | `test_log_written`, `test_corrupt_log` |

---

## Out of Scope

- WRK-635 `scan-sessions.py` implementation (separate WRK).
- Memory file content decisions (what to keep/evict) — only the governance mechanism.
- `curate-memory.py` full Phase 3c integration (script only; cron wiring deferred).
- Memory quality eval harness (% stale, % verified, signal density, usage tracking) → spin off as WRK-638.

---

## Gemini Notes

As a systems reliability agent, here are the critical findings based on your review criteria:

1. **Failure modes in L3 gemini output parsing:** 
   `curate-memory.py` relies on LLM output which is inherently non-deterministic. If the LLM returns partial YAML, fenced code blocks, or conversational prose ("Here is the classification..."), a naive parser will crash.
   *Resolution:* The refined plan introduces strict regex extraction, automated stripping of markdown fences, and a fail-safe fallback to the `memory-keep` category to prevent data loss when parsing fails.

2. **Carry-forward logic (`portfolio-signals.yaml` & core files missing/corrupt):** 
   If external state files (like a `portfolio-signals.yaml`), `compact-log.jsonl`, or even the `archive/` directories are missing or corrupt, a brittle script will halt the entire automated pipeline.
   *Resolution:* Added tests and implementation details to handle missing/corrupt files gracefully. Corrupt JSON logs will be backed up and re-initialized. Missing directories will be created on the fly.

3. **Thresholds & Tie-Breaks (Engineering >= Harness / Dual-Mode):** 
   While the prompt mentions an "engineering >= harness" tie-break, in the context of memory compaction, the critical thresholds are the 80% dedup overlap and the >30 days done-WRK expiry. 80% token overlap might incorrectly flag technical bullets that share boilerplate command syntax but have different core facts.
   *Resolution:* Acknowledged the threshold risk. Recommended falling back to semantic similarity or ensuring dedup favors the *fresher* signal strictly without deleting highly technical but structurally similar context.

4. **Test coverage (16 tests for AC surface area):** 
   The original draft only specified 7 basic "happy path" or primary feature tests. This is vastly insufficient for a script that destructively modifies core agent memory.
   *Resolution:* Expanded the test strategy table from 7 to 16 tests, heavily weighting failure modes (timeouts, corrupt files, concurrent locks, bad LLM output, regex failures).

5. **Nightly Cron Risks:**
   Running memory compaction blindly via cron introduces three major risks:
   - **File lock races:** The agent might be writing to `MEMORY.md` at the exact moment the cron job attempts to compact it, resulting in truncated files.
   - **3 AM Quotas:** Gemini CLI limits might be hit during batch processing in `curate-memory.py`.
   - **Partial Writes:** Server restarts or OOM kills during file updates.
   *Resolution:* The plan now explicitly mandates **atomic renames** (write to `.tmp`, then `mv`), **file locking** (`.lock` files), and graceful exits on quota limits to ensure cron runs are completely bulletproof.
