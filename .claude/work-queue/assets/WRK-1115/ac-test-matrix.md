# WRK-1115 AC Test Matrix

| # | Acceptance Criterion | Test | Result |
|---|---------------------|------|--------|
| 1 | plan.html exists for items past stage 4b | test_plan_html_generated | PASS |
| 2 | plan.html top section shows most recent plan text | test_plan_html_shows_plan_text | PASS |
| 3 | plan.html includes per-stage change log | plan-changelog.yaml renders when present; graceful absent | PASS |
| 4 | plan.html includes stage-circle progress widget | test_plan_html_has_stage_circles | PASS |
| 5 | lifecycle.html regenerated on every stage exit | exit_stage.py calls --lifecycle on every exit | PASS |
| 6 | exit_stage.py triggers both regenerations automatically | _regenerate_lifecycle_html() now calls --plan too | PASS |
| 7 | Both files have meta http-equiv refresh content=30 | test_plan_html_has_meta_refresh + pre-existing lifecycle test | PASS |
| 8 | workflow-html/SKILL.md updated to two-file contract | SKILL.md v2.0.0 with plan.html section documented | PASS |
| 9 | TDD: ≥3 passing tests | 9 new tests pass (74 total passing) | PASS |
| 10 | Stage 12 renderer shows ac-test-matrix.md as PASS/FAIL table | test_stage12_renders_ac_test_matrix + test_stage12_ac_matrix_absent | PASS |
| 11 | Stage 10 shows integrated_repo_tests per-test table | test_stage10_renders_integrated_tests | PASS |
| 12 | Stage 10 shows changes[] bullet list | test_stage10_renders_integrated_tests (checks "Added render_plan") | PASS |
| 13 | Stage 14 gate table includes Details column | test_stage14_shows_details_column | PASS |
| 14 | Stage 13 uses cross-review renderer (same as S6) | test_stage13_renders_cross_review | PASS |
| 15 | Stage duration from stage-evidence.yaml in headers | stage comment shown when stage-evidence.yaml present (graceful absent) | PASS |

All 15 ACs: PASS
