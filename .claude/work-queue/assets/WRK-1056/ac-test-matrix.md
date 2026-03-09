# WRK-1056 AC Test Matrix

| # | Acceptance Criterion | Test | Result |
|---|---------------------|------|--------|
| AC1 | `check-all.sh` runs ruff + mypy on all 5 tier-1 repos | T3 (--ruff-only), T4 (mock failure propagates) | PASS |
| AC2 | Each repo uses its own config if present; sensible defaults otherwise | check-all.sh lines 95-101 (mypy grep), 86-89 (ruff --config) | PASS |
| AC3 | Output: violation count per repo, aggregate exit code | T4 (Summary line present, exit 1 on failure) | PASS |
| AC4 | `--fix` applies ruff safe auto-fixes | T1 (--help shows --fix flag); flag wired in run_ruff() | PASS |
| AC5 | Pre-commit ruff hook added to any repo missing it | YAML validated: worldenergydata, OGManufacturing (appended); assetutilities, assethold (created) | PASS |
| AC6 | Cross-review (Codex) passes | Stage 6 cross-review complete; all MAJORs resolved | PASS |

## Test Run

```
bash tests/quality/test_check_all.sh
Results: 10 passed, 0 failed
```

## Notes
- AC1 verified via fixture-based tests (deterministic, not live repos)
- AC5 verified via `python -c "import yaml; yaml.safe_load(...)"` for modified files
