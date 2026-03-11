# WRK-1081 Implementation Cross-Review Package

## Summary
Extended `scripts/quality/check-all.sh` with bandit (security), radon (complexity),
and vulture (dead code) checks across all 5 tier-1 Python repos.

## Files Changed

### scripts/quality/check-all.sh
- New flags: `--bandit`, `--radon`, `--vulture`, `--static`
- `run_bandit()`: two-pass (Pass 1 = LOW warn/non-blocking; Pass 2 = MEDIUM+ gate with `-ll -b baseline`)
- `run_radon()`: `uvx radon==6.0.1 cc src/ -n C || true` (warn-only)
- `run_vulture()`: `uvx vulture==2.15 src/ --min-confidence 80 || true` (warn-only)
- `_bandit_baseline()`: resolves `config/quality/bandit-baseline-{repo}.json`
- LOW WARN lines printed directly to stdout (not captured in subshell)

### tests/quality/test_check_all_static.sh (new)
- 12 tests, 23 assertions — all GREEN
- Mock `uvx` handles `-ll` flag semantics
- Mock `uv` passes `run --no-project python` to actual python3

### config/quality/bandit-baseline-{repo}.json (5 files)
- Empty JSON baselines: `{"results":[],"metrics":{}}`

### {repo}/pyproject.toml (5 repos)
- Added `[tool.bandit]` with `exclude_dirs = ["tests", "docs"]`

### {repo}/.radon.cfg (5 repos)
- Radon config: `[radon] / cc_min = C`

### {repo}/vulture_whitelist.py (5 repos)
- Empty whitelist stub for known false positives

### {repo}/.pre-commit-config.yaml (3 repos: assetutilities, assethold, OGManufacturing)
- Added local `bandit-staged` hook: `uvx bandit[toml]==1.9.4 -ll -c pyproject.toml`
- digitalmodel and worldenergydata already had bandit hooks

## Key Design Decisions
1. Two-pass bandit: Pass 1 for LOW warnings; Pass 2 for MEDIUM+ gate
2. LOW warn lines go to stdout directly (not captured in `$(...)`) 
3. `uv run --no-project python` for all Python invocations (workspace rule)
4. Tool version pins: `bandit[toml]==1.9.4`, `radon==6.0.1`, `vulture==2.15`
5. Native baseline format (`-b baseline.json`) for suppressing existing findings
6. radon and vulture always non-blocking (`|| true`)

## Test Results
- test_check_all_static.sh: 23/23 PASS
- test_check_all.sh: 35/35 PASS (no regressions)
