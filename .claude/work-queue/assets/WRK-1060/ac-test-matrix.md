# AC Test Matrix — WRK-1060

Generated: 2026-03-11

## TDD Tests

| Test | Status | Notes |
|------|--------|-------|
| test_classify_covered_dir | PASS | src/ → covered |
| test_classify_uncovered_dir | PASS | scripts/ → uncovered |
| test_classify_partial_dir_notebooks | PASS | notebooks/ in assethold → uncovered |
| test_classify_partial_dir_notebooks_digitalmodel | PASS | notebooks/ in digitalmodel → partial |
| test_all_repos_walked | PASS | REPO_MAP has all 5 repos |
| test_yaml_output_schema | PASS | required keys present |
| test_classify_unknown_dir | PASS | vendor/ → unknown |
| test_gap_count_matches | PASS | summary.total_gaps == counted |

**Total: 8/8 PASS**

## Acceptance Criteria

| AC | Criteria | Status |
|----|----------|--------|
| AC1 | Gap discovery script walks all 5 repos | PASS |
| AC2 | Uncovered dirs/file types listed with check tool recommendation | PASS |
| AC3 | Gap report YAML produced | PASS — `config/quality/quality-gap-report.yaml` (25 dir gaps) |
| AC4 | At least one gap addressed with concrete new check | PASS — `check-all.sh --gap` flag |
| AC5 | Codex cross-review passes | PASS — HIGH finding (worldenergydata false positives) fixed |
