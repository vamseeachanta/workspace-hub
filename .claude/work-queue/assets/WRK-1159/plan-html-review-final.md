confirmed_by: vamsee
confirmed_at: 2026-03-13T03:18:00Z
decision: passed

## WRK-1159 Plan Final Review

3 changes to `start_stage.py`:
1. Extend `_regenerate_lifecycle_html()` to generate both `--lifecycle` and `--plan` HTML
2. Add `_auto_open_html_for_human_gates()` with stage map {5: plan_draft, 7: plan_final, 17: close_review}
3. Wire the call after `_regenerate_lifecycle_html()` in `_main()`

TDD: 6 test cases (9 runs with parametrize), all passing.
