# WRK-1092 Plan — Mypy Error Count Ratchet (updated post cross-review)

## Route A (simple) — inline plan

### Step 1: Baseline capture (`--init` mode)
- `check_mypy_ratchet.py --init` runs mypy per repo, parses error count, writes `config/quality/mypy-baseline.yaml`
- `--init` is idempotent: re-running updates all counts

### Step 2: `scripts/quality/check_mypy_ratchet.py`
- Modes: `--init` (capture baseline), default (ratchet check)
- Load `config/quality/mypy-baseline.yaml`; run mypy per repo; parse "Found N errors" / "Success: no issues found"
- FAIL if count > baseline; PASS + auto-update baseline YAML if count < baseline; PASS if equal
- Missing baseline file → actionable error message
- Mypy not installed → SKIP with warning (not FAIL)
- `SKIP_MYPY_REASON` env var → bypass all checks (logged)

### Step 3: `check-all.sh --mypy-ratchet` flag
- Calls `check_mypy_ratchet.py --baseline config/quality/mypy-baseline.yaml`

### Step 4: Pre-push hook integration (opt-in)
- Extend `scripts/hooks/pre-push.sh` with mypy ratchet check
- Gated by `MYPY_RATCHET_GATE=1` env var (opt-in; avoids 60-180s blocking all pushes)

### Step 5: TDD (≥10 tests in `tests/quality/test_check_mypy_ratchet.py`)
1. Baseline YAML schema validation (valid)
2. Baseline YAML schema validation (invalid — missing fields)
3. Parse "Found N errors in M files" → N
4. Parse "Found 1 error in 1 file" → 1
5. Parse "Success: no issues found" → 0
6. Ratchet FAIL (count increased)
7. Ratchet PASS (count equal)
8. Ratchet PASS + auto-update baseline (count decreased)
9. Missing baseline file → clear error
10. SKIP_MYPY_REASON env var bypass
11. `--init` mode writes baseline with correct counts

### Auto-update behavior
Writes updated YAML only — developer stages and commits. No auto-commit.

### Acceptance Criteria
- `config/quality/mypy-baseline.yaml` exists with error counts for all 5 repos
- `check_mypy_ratchet.py --init` seeds the baseline
- Ratchet check fails if count increased, passes + updates if decreased
- Pre-push hook updated (opt-in via `MYPY_RATCHET_GATE=1`)
- `check-all.sh --mypy-ratchet` works
- ≥10 TDD tests pass
- Script passes ruff + mypy itself
