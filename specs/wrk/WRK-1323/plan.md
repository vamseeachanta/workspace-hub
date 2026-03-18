# WRK-1323 Plan: Add --dry-run flag to verify_checklist.py

## ACs
1. verify_checklist.py accepts --dry-run flag
2. --dry-run prints checklist items without checking evidence files
3. --dry-run returns exit code 0 regardless of evidence state
4. Normal mode behavior unchanged

## Implementation
1. Add --dry-run argparse flag (store_true)
2. Pass dry_run to verify_checklist() function
3. Short-circuit: if dry_run, return items without validation
4. CLI: print items and exit 0 in dry-run mode

## Tests
10 TDD tests in scripts/work-queue/tests/test_verify_checklist.py
