# WRK-1093 Plan — Documentation Drift Detector

## Summary
Detect when public API symbols drift from their documentation and surface gaps as WRK items.

## Approach

### Phase 1 — TDD (tests first, all RED)
File: `tests/quality/test_check_doc_drift.py` — 6 tests:
1. `test_load_symbol_index_reads_jsonl` — reads symbol-index.jsonl, returns list of dicts
2. `test_build_doc_mention_set_from_readme` — scans README.md → set of symbol names
3. `test_compute_drift_score_all_documented` → score = 0.0
4. `test_compute_drift_score_none_documented` → score = 1.0
5. `test_detect_staleness_flags_changed_file` — git log mtime > docs mtime → stale=True
6. `test_auto_wrk_triggered_when_drift_increases` — drift > baseline → returns WRK capture string

### Phase 2 — Implementation
File: `scripts/quality/check_doc_drift.py`
- `load_symbol_index(path: Path) -> list[dict]` — reads JSONL
- `build_doc_mention_set(repo_path: Path) -> set[str]` — single grep pass over docs/ + README.md
- `compute_drift_score(symbols: list[dict], doc_mentions: set[str], repo: str) -> float`
- `detect_staleness(file_path: str, docs_path: Path, repo_path: Path) -> bool`
- `run_drift_check(repos: list[str], ...) -> dict` — orchestrator
- `auto_wrk_if_drift_increased(report: dict, baseline: dict) -> list[str]`
- CLI with argparse: `--repo`, `--update-baseline`, `--format json|text`

### Phase 3 — Baseline + Integration
- `config/quality/doc-drift-baseline.yaml` — initial per-repo drift scores
- `check-all.sh --drift` flag → calls `check_doc_drift.py` (warn-only, exit 0)
- `logs/quality/.gitkeep`

### Phase 4 — Cron + Cross-review
- `scripts/cron/crontab-template.sh`: `30 2 * * * ... check_doc_drift.py --update-baseline`
- Cross-review with Codex + Gemini; fix MAJOR findings

## Files Modified
- `scripts/quality/check_doc_drift.py` (new)
- `tests/quality/test_check_doc_drift.py` (new)
- `config/quality/doc-drift-baseline.yaml` (new)
- `scripts/quality/check-all.sh` (extend --drift flag)
- `scripts/cron/crontab-template.sh` (add cron entry)
- `logs/quality/.gitkeep` (new)

## Risks
- R1: Symbol index lacks git timestamps → use subprocess git log per file (cached)
- R2: 22k symbols → build inverted doc-mention set once, O(1) lookup per symbol
