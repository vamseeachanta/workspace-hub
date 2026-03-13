# WRK-1128 Plan Final Review

confirmed_by: vamsee
confirmed_at: 2026-03-13T09:28:00Z
decision: passed

## Plan: Observed-Exposure Tracker

Script `scripts/ai/observed_exposure_report.py`:
1. `scan_wrk_files()` — glob pending/working/archive .md, parse YAML frontmatter
2. `classify_stages()` — binary: stages {1,5,7,17} = human, rest = AI
3. `aggregate_by_category()` — group + sum per category
4. `format_table()` — Markdown or CSV with observed % + theoretical max %
5. CLI: `--csv`, `--queue-root`

TDD: 9 tests (empty queue, full lifecycle, mixed categories, partial stages, missing evidence, CSV, markdown, archive, constant check)
