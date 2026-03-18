# WRK-1323 Plan (Claude)

Route A simple — add `--dry-run` flag to `verify_checklist.py`.

1. Add `--dry-run` argparse flag
2. Pass to `verify_checklist()` as `dry_run` param
3. Skip evidence validation when `dry_run=True`
4. Print checklist items and exit 0 in dry-run CLI mode
5. Write TDD tests covering happy/edge/error paths
