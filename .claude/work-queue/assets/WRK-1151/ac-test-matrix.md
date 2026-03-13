wrk_id: WRK-1151
tdd_applicable: false
rationale: >
  WRK-1151 is a research/download task (Route B). No application code was written.
  TDD is not applicable. Validation was performed via:
  - Download script dry-run (bash scripts/data/naval-architecture/download-naval-arch-docs.sh --dry-run)
  - Document-index integrity check (uv run --no-project python scripts/data/document-index/phase-e2-remap.py --check)
  - Legal sanity scan (bash scripts/legal/legal-sanity-scan.sh)
test_count: 0
test_pass: 0
test_fail: 0
