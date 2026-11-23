# WRK-1323: Add --dry-run flag to verify_checklist.py

## Context
`verify_checklist.py` validates whether a WRK item's checklist evidence exists for a given stage.
The CLI requires `WRK-NNN STAGE` and reads `evidence/checklist-{NN}.yaml`. During checklist
authoring/debugging, you need to preview what items a stage would check — without needing
real evidence files. The `--dry-run` flag satisfies this.

## Implementation Plan (TDD)

### Phase 1 — Tests (write first, must fail)

File: `tests/work-queue/test_transition_hardening.py`

Add class `TestDryRun` with 4 tests:
1. `test_dry_run_no_checklist` — stage YAML with no checklist key → passes, prints 0-item message
2. `test_dry_run_prints_all_items` — stage with 3 checklist items → prints all 3 items, result shows them
3. `test_dry_run_no_evidence_required` — evidence dir does not exist → still passes (no FileNotFoundError)
4. `test_dry_run_does_not_validate` — evidence file absent but dry_run=True → passes (not blocked)

### Phase 2 — Implementation

File: `scripts/work-queue/verify_checklist.py`

**Changes to `verify_checklist()` function:**
- Add `dry_run: bool = False` parameter
- When `dry_run=True`: skip reading evidence file; return `{"passed": True, "blockers": [], "items": [...]}`
  where `items` is the list of checklist dicts from the stage YAML

**Changes to CLI (`__main__` block):**
- Replace bare `sys.argv` parsing with `argparse`
- New usage: `verify_checklist.py [--dry-run] WRK-NNN STAGE`
- When `--dry-run`: call `verify_checklist(..., dry_run=True)`, then print each item and exit 0

### CLI Output Format (--dry-run)
```
DRY-RUN: stage 10 has 5 checklist items:
  CL-10-1  Scripts-over-LLM audit performed
  CL-10-2  Tests written BEFORE implementation (TDD Red)
  CL-10-3  Implementation follows TDD Green cycle
  CL-10-4  No scope creep beyond WRK acceptance criteria
  CL-10-5  All linters pass (ruff/mypy if applicable)
```
Exit 0 always in dry-run mode.

## Critical Files
- `scripts/work-queue/verify_checklist.py` — main change
- `tests/work-queue/test_transition_hardening.py` — new TestDryRun class
- `scripts/work-queue/stages/stage-10-work-execution.yaml` — sample for test fixtures

## Verification
```bash
# Run new tests (must pass)
uv run --no-project python -m pytest tests/work-queue/test_transition_hardening.py -v -k TestDryRun

# Run full test file (must not regress)
uv run --no-project python -m pytest tests/work-queue/test_transition_hardening.py -v

# Manual smoke test
uv run --no-project python scripts/work-queue/verify_checklist.py --dry-run WRK-1323 10
uv run --no-project python scripts/work-queue/verify_checklist.py --dry-run WRK-1323 7
```
