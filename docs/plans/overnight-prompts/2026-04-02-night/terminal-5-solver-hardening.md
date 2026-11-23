# Terminal 5 — Solver Queue Hardening + Automation
# Provider: Claude/Hermes (pipeline/tool building)
# Issues: #1654, #1650, #1648
# Est. Time: 2-3 hours

We are in /mnt/local-analysis/workspace-hub. This repo's solver queue scripts are
at `scripts/solver/`. Solver queue tests go in `tests/solver/`.

Use `uv run` for all Python — never bare `python3` or `pip`.
Do NOT ask the user any questions. Work autonomously.
Do NOT branch — commit to `main` and push after each task.
Run `git pull origin main --rebase` before every push (stash if needed).
TDD mandatory: write tests BEFORE implementation.
Mock all external dependencies — do NOT require network, licenses, Windows machines, or mounts.

IMPORTANT: Do NOT write to any of these paths (owned by other terminals):
- digitalmodel/src/digitalmodel/cathodic_protection/ (Terminal 1)
- digitalmodel/tests/cathodic_protection/ (Terminal 1)
- digitalmodel/src/digitalmodel/ansys/ (Terminal 2)
- digitalmodel/tests/ansys/ (Terminal 2)
- digitalmodel/src/digitalmodel/fatigue/ (Terminal 3)
- digitalmodel/tests/fatigue/ (Terminal 3)
- digitalmodel/src/digitalmodel/web/ (Terminal 4)
- digitalmodel/src/digitalmodel/reservoir/ (Terminal 4)
- digitalmodel/pyproject.toml (Terminal 4)
- docs/dashboards/ (Terminal 4)
- scripts/document-intelligence/ (Terminal 4)

Only write to:
- scripts/solver/
- tests/solver/
- config/cron/ (new cron entries if needed)
- docs/solver/ (documentation)

---

## TASK 1: Solver Queue — Retry Logic + Exponential Backoff (#1654)
GH Issue: #1654

The solver queue currently has no retry mechanism. When a job fails on
licensed-win-1, it stays failed. We need automatic retry with backoff.

### Existing files to review first:
- scripts/solver/process-queue.py
- scripts/solver/submit-job.sh
- scripts/solver/queue-health.sh

### Implementation:
1. Read process-queue.py to understand current job lifecycle
2. Write tests: `tests/solver/test_retry_logic.py`
   - Test retry on transient failure (connection timeout, file lock)
   - Test exponential backoff timing (1s, 2s, 4s, 8s, max 60s)
   - Test max retry count (default 3, configurable)
   - Test permanent failure detection (license error, invalid model)
   - Test retry state persistence (JSONL log)
   - Test that successful retry clears retry counter
   - At least 8 test cases
3. Implement: `scripts/solver/retry_handler.py`
   - `RetryConfig` dataclass (max_retries=3, base_delay=1.0, max_delay=60.0)
   - `should_retry(error: str) -> bool` — classify transient vs permanent
   - `get_backoff_delay(attempt: int, config: RetryConfig) -> float`
   - `record_retry(job_id, attempt, error, log_path)` — append to JSONL
   - `RetryHandler` class that wraps job submission
4. Verify: `uv run pytest tests/solver/test_retry_logic.py -v`

Commit message: `feat(solver): retry logic with exponential backoff for failed jobs (#1654)`

---

## TASK 2: Solver Queue — Batch Manifest Validation CLI (#1650)
GH Issue: #1650

Need a CLI tool to validate batch manifests before submission.

### Existing files to review:
- scripts/solver/batch-manifest.yaml.example
- scripts/solver/submit-batch.sh

### Implementation:
1. Write tests: `tests/solver/test_manifest_validator.py`
   - Test valid manifest passes validation
   - Test missing required fields (model_file, solver_type)
   - Test invalid file references (model file doesn't exist)
   - Test duplicate job names in manifest
   - Test invalid solver type
   - Test schema version compatibility
   - At least 8 test cases
2. Implement: `scripts/solver/validate_manifest.py`
   - `ManifestSchema` Pydantic model for batch manifest
   - `validate_manifest(path: Path) -> ValidationResult`
   - `check_file_references(manifest, base_dir) -> list[str]` — warnings for missing files
   - `check_duplicates(manifest) -> list[str]` — duplicate job names
   - CLI entrypoint: `uv run python scripts/solver/validate_manifest.py path/to/manifest.yaml`
   - Exit 0 on valid, exit 1 on invalid with clear error messages
3. Verify: `uv run pytest tests/solver/test_manifest_validator.py -v`

Commit message: `feat(solver): batch manifest validation CLI with schema enforcement (#1650)`

---

## TASK 3: Solver Queue — Watch-Results Cron Integration + JSONL Dashboard (#1648)
GH Issue: #1648

Integrate watch-results.sh into cron schedule and add a JSONL-based dashboard.

### Existing files to review:
- scripts/solver/watch-results.sh
- scripts/solver/queue-health.sh
- config/cron/schedule-tasks.yaml

### Implementation:
1. Write tests: `tests/solver/test_results_dashboard.py`
   - Test JSONL parsing from watch-results output
   - Test dashboard summary generation (total/pass/fail/pending)
   - Test time-series aggregation (jobs per day)
   - Test markdown report generation
   - At least 6 test cases
2. Implement: `scripts/solver/results_dashboard.py`
   - `parse_results_log(jsonl_path: Path) -> list[JobResult]`
   - `generate_summary(results: list[JobResult]) -> DashboardSummary`
   - `generate_markdown_report(summary: DashboardSummary) -> str`
   - Write report to `docs/solver/queue-dashboard.md`
3. Add cron entry to `config/cron/schedule-tasks.yaml`:
   - watch-results: every 4 hours on ace-linux-1
   - dashboard regeneration: daily at 05:00 UTC
4. Document setup in `docs/solver/README.md` (create if not exists)
5. Verify: `uv run pytest tests/solver/test_results_dashboard.py -v`

Commit message: `feat(solver): results dashboard + cron integration for watch-results (#1648)`

---

After all tasks, post progress comments:
```
gh issue comment 1654 --repo vamseeachanta/workspace-hub --body "Terminal 5 overnight: retry logic implemented with exponential backoff. Max 3 retries, 1s/2s/4s delays, JSONL logging. Transient vs permanent failure classification included."

gh issue comment 1650 --repo vamseeachanta/workspace-hub --body "Terminal 5 overnight: batch manifest validator CLI complete. Pydantic schema, file reference checks, duplicate detection. Usage: uv run python scripts/solver/validate_manifest.py <path>"

gh issue comment 1648 --repo vamseeachanta/workspace-hub --body "Terminal 5 overnight: JSONL results dashboard + cron entries added. Dashboard at docs/solver/queue-dashboard.md, cron in config/cron/schedule-tasks.yaml."
```
