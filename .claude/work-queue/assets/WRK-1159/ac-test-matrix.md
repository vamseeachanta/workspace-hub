# AC Test Matrix — WRK-1159

| AC | Test | Status | Evidence |
|----|------|--------|----------|
| Auto-open at stages 5, 7, 17 | test_auto_open_calls_browser_script | PASS | test_auto_open_html.py |
| Cross-platform opening | test_open_linux_xdg_open | PASS | test_auto_open_html.py |
| Evidence written per file | test_evidence_written | PASS | test_auto_open_html.py |
| HTML regen before open | test_regenerate_before_open | PASS | test_auto_open_html.py |
| No double-open | test_no_double_open_if_evidence_exists | PASS | test_auto_open_html.py |
| Non-gate stages skipped | test_non_gate_stages_skipped | PASS | test_auto_open_html.py |
| Missing HTML graceful | test_missing_html_graceful | PASS | test_auto_open_html.py |
| Missing script graceful | test_missing_script_warns | PASS | test_auto_open_html.py |
| Both files opened | test_both_lifecycle_and_plan_opened | PASS | test_auto_open_html.py |

**Summary:** 9 PASS, 0 FAIL
