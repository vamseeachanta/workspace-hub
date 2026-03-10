# WRK-1091 AC Test Matrix

| # | Acceptance Criterion | Test | Status |
|---|---------------------|------|--------|
| 1 | `config/deps/cross-repo-graph.yaml` exists with correct structure | `test_graph_yaml_exists`, `test_graph_yaml_has_required_keys` | PASS |
| 2 | `scripts/testing/run-cross-repo-integration.sh` runs combined test suite | `test_script_exists_and_is_executable`; manual run all 3 repos pass | PASS |
| 3 | Pre-push hook triggers cross-repo run (version-controlled) | scripts/hooks/assetutilities-pre-push.sh + .pre-commit-config.yaml stages:push | PASS |
| 4 | Exit code 1 + clear report when downstream breaks detected | `test_script_exits_1_on_unknown_repo`; bypass test `test_skip_env_var_bypasses_checks` | PASS |
| 5 | ≥5 TDD tests (graph loading, combined run logic, break detection, report format) | 6 unit tests all PASS | PASS |
| 6 | Passes `check-all.sh` for any Python components | ruff check: all checks passed | PASS |

## Summary
- PASS: 6
- FAIL: 0
