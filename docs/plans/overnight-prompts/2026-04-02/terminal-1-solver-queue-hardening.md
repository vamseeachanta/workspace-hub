# Terminal 1 — Solver Queue Hardening + OrcaFlex Test Coverage

Provider: **Claude** (high-context synthesis, cross-file reading)
Issues: #1586, #1595, #1628 (sprint plan Phase 1)

---

We are in /mnt/local-analysis/workspace-hub. Execute these 3 tasks in order.
Use `uv run` for all Python — never bare python3. Commit to main and push after each task.
Do not branch. TDD: write tests before implementation.
Do NOT ask the user any questions. Run `git pull origin main` before every push.

IMPORTANT: Do NOT write to docs/architecture/, docs/roadmaps/, docs/dashboards/,
digitalmodel/tests/structural/, digitalmodel/tests/subsea/, digitalmodel/tests/naval_architecture/,
digitalmodel/tests/asset_integrity/, digitalmodel/tests/data_systems/,
scripts/analysis/, scripts/docs/, scripts/document-intelligence/ — those are owned by
other terminals. Only write to: scripts/solver/, digitalmodel/tests/orcaflex/,
digitalmodel/tests/solver/, data/solver-manifests/.

---

## TASK 1: Batch Submission Script (GH issue #1595)

**Context**: `scripts/solver/submit-job.sh` exists and handles single job submission.
We need a batch wrapper that reads a YAML manifest and submits multiple jobs.

**Acceptance criteria**:
1. Create `scripts/solver/submit-batch.sh` — reads YAML manifest, calls submit-job.sh per entry
2. Create `scripts/solver/batch-manifest.yaml.example` — example manifest with 3+ jobs
3. Create `tests/solver/test_batch_submission.py` — unit tests that validate:
   - YAML manifest parsing
   - Job count extraction
   - Error handling for missing fields
   - Dry-run mode (--dry-run flag)
4. Mock all git/filesystem operations in tests — do NOT require actual solver or git push
5. Tests must pass: `uv run pytest tests/solver/test_batch_submission.py -v`

**Commit message**: `feat(solver): batch submission script with YAML manifest (#1595)`

---

## TASK 2: Result Watcher + Post-Processing Hook (GH issue #1586)

**Context**: Completed OrcaWave jobs land in `queue/completed/`. We need automated
watching and post-processing.

**Acceptance criteria**:
1. Create `scripts/solver/watch-results.sh` — polls queue/completed/ for new .yaml results,
   triggers post-process-hook.py for each
2. Create `scripts/solver/post-process-hook.py` — extracts key metrics from completed job YAML,
   appends summary to `data/solver-results-log.jsonl`
3. Create `scripts/solver/queue-health.sh` — reports: pending count, last completed timestamp,
   failed jobs count, queue age stats
4. Create `tests/solver/test_result_watcher.py` — tests with fixture YAML files:
   - Successful job detection
   - Failed job handling
   - JSONL append behavior
   - Health report format
5. Create `tests/solver/test_queue_health.py` — tests for queue health reporting
6. All tests mock filesystem — no real queue directory needed
7. Tests pass: `uv run pytest tests/solver/ -v`

**Commit message**: `feat(solver): result watcher + post-processing hook + queue health (#1586)`

---

## TASK 3: OrcaFlex Test Coverage Uplift (related to #1602)

**Context**: `digitalmodel/src/digitalmodel/orcaflex/` has 14 source files but only 1 test file.
This blocks PRODUCTION promotion. Need 5+ test files total.

**Source files to cover**:
- `orcaflex/qa.py`
- `orcaflex/reporting/builder.py`
- `orcaflex/reporting/config.py`
- `orcaflex/reporting/sections/code_check.py`
- `orcaflex/reporting/sections/modal_analysis.py`
- `orcaflex/reporting/sections/model_summary.py`
- `orcaflex/reporting/sections/mooring_loads.py`
- `orcaflex/reporting/sections/qa_summary.py`
- `orcaflex/reporting/sections/range_graphs.py`
- `orcaflex/reporting/sections/static_config.py`
- `orcaflex/reporting/sections/time_series.py`

**Acceptance criteria**:
1. Create `digitalmodel/tests/orcaflex/test_qa.py` — test QA module
2. Create `digitalmodel/tests/orcaflex/test_report_builder.py` — test OrcaFlexReportBuilder
3. Create `digitalmodel/tests/orcaflex/test_config.py` — test all config dataclasses
4. Create `digitalmodel/tests/orcaflex/reporting/test_sections.py` — test report sections
5. Mock OrcFxAPI and any external dependencies — tests must run without licenses
6. Each test file must have at least 5 test functions
7. Total: 6+ test files (including existing 1), meeting PRODUCTION threshold
8. Tests pass: `uv run pytest digitalmodel/tests/orcaflex/ -v`

**Commit message**: `test(orcaflex): test coverage uplift — 1 → 6+ test files, targeting PRODUCTION (#1602)`

---

Post a brief progress comment on GH issues #1586, #1595, #1628 when complete.
