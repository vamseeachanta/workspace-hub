# WRK-1060: Quality Gap Discovery

## Context

Quality checks across the 5 tier-1 repos (assetutilities, digitalmodel, worldenergydata,
assethold, OGManufacturing) are inconsistent. `check-all.sh` and per-repo `.pre-commit-config.yaml`
cover `src/` and `tests/` well, but `scripts/`, `examples/`, and config directories are
completely uncovered. Ratchet gates (mypy, complexity) exist as hub scripts but are not
wired into any repo's pre-commit. This WRK creates a gap discovery script and produces
a canonical YAML gap report for the ecosystem.

## Route

**Route B** (medium) — exploration + script creation + one concrete gap addressed.

## Plan

### Step 1 — TDD: Write tests first
File: `scripts/quality/tests/test_quality_gap_report.py`

Tests (≥6, all PASS before implementation):
- `test_classify_covered_dir` — src/ maps to ruff+mypy → "covered"
- `test_classify_uncovered_dir` — scripts/ maps to no checks → "uncovered"
- `test_classify_partial_dir` — notebooks/ in digitalmodel → "partial"
- `test_all_repos_walked` — scanner finds all 5 repos given REPO_MAP
- `test_yaml_output_schema` — output YAML has required keys: repo, dirs, file_types, gaps
- `test_gap_count_matches` — gap_count in summary == len(gaps in YAML)

### Step 2 — Implement `quality-gap-report.py`
File: `scripts/quality/quality-gap-report.py`

```
Usage: uv run --no-project python scripts/quality/quality-gap-report.py [--repo <name>] [--output <path>]
Output: gap report YAML + human-readable summary to stdout
```

**Coverage map** (hardcoded from resource-intelligence):
```python
COVERAGE_MAP = {
    "src/": ["ruff", "mypy", "pytest", "bandit"],
    "tests/": ["ruff", "pytest"],
    "scripts/": [],           # gap: no checks in any repo
    "examples/": [],          # gap: no checks
    "notebooks/": [],         # gap: only digitalmodel has nbqa
    "docs/": ["markdownlint"],# partial: only digitalmodel/worldenergydata
    "config/": [],            # gap: no YAML schema validation
}
```

**Logic**:
1. Walk each repo top-level dirs against COVERAGE_MAP
2. For `digitalmodel`: upgrade notebooks/ to "partial" (nbqa present)
3. For `worldenergydata`: upgrade docs/ to "partial" (markdownlint present)
4. Collect uncovered dirs per repo, annotate with recommended tool
5. Output `config/quality/quality-gap-report.yaml`
6. Print human-readable summary table to stdout

**YAML schema**:
```yaml
schema_version: "1"
generated_at: <ISO timestamp>
repos:
  assetutilities:
    dirs:
      scripts/: {coverage: uncovered, recommended_tool: ruff, effort: low}
      examples/: {coverage: uncovered, recommended_tool: ruff, effort: low}
    cross_cutting_gaps:
      - pydocstyle_missing
      - radon_missing
      - windows_path_guard_missing
  ...
summary:
  total_gaps: 13
  high_effort_gaps: 2
  low_effort_gaps: 11
```

### Step 3 — Wire into check-all.sh
Add `--gap` flag to `check-all.sh` that calls `quality-gap-report.py`.
Existing REPO_MAP and flag pattern (OPT_GAP) to mirror.

### Step 4 — Run and commit gap report
```bash
uv run --no-project python scripts/quality/quality-gap-report.py
# → config/quality/quality-gap-report.yaml
```
Commit report as a tracked artifact.

### Step 5 — Address one concrete gap
Add `scripts/` to ruff `include` in **assethold** and **assetutilities** `pyproject.toml`
(both already use ruff; extending to cover scripts/ is low-effort, low-risk).

This directly resolves the most universal gap (scripts/ uncovered).

### Step 6 — Codex cross-review
Write `scripts/review/results/wrk-1060-phase-1-review-input.md` and run:
```bash
bash scripts/review/cross-review.sh scripts/review/results/wrk-1060-phase-1-review-input.md all
```

## Files to Create/Modify

| Action | Path |
|--------|------|
| CREATE | `scripts/quality/quality-gap-report.py` |
| CREATE | `scripts/quality/tests/test_quality_gap_report.py` |
| CREATE | `config/quality/quality-gap-report.yaml` (generated) |
| MODIFY | `scripts/quality/check-all.sh` (add `--gap` flag) |
| MODIFY | `assethold/pyproject.toml` (extend ruff include to scripts/) |
| MODIFY | `assetutilities/pyproject.toml` (extend ruff include to scripts/) |

## Reuse

- `scripts/quality/api-audit.py` — structural pattern (REPO_MAP, walk-and-classify, JSON output)
- `scripts/quality/check-all.sh` — existing REPO_MAP and flag scaffolding
- `scripts/quality/tests/test_check_complexity_ratchet.py` — test structure pattern

## Verification

```bash
# Run tests (must all PASS before implementation)
uv run --no-project python -m pytest scripts/quality/tests/test_quality_gap_report.py -v

# Run gap report
uv run --no-project python scripts/quality/quality-gap-report.py

# Verify YAML output
cat config/quality/quality-gap-report.yaml

# Verify check-all.sh integration
bash scripts/quality/check-all.sh --gap --repo assetutilities

# Verify ruff now covers scripts/ in assethold
cd assethold && uv run ruff check scripts/ --no-cache
```
