# WRK-1094 AC Test Matrix

| AC | Test | Result |
|----|------|--------|
| check_config_drift.py exists and runs | test_line_limit_pass | PASS |
| Line limit: new regression → error exit | test_line_limit_regression | PASS |
| Line limit: known baseline debt → warn | test_line_limit_warn | PASS |
| AGENTS.md frontmatter absent → error | test_agents_fm_missing | PASS |
| AGENTS.md frontmatter valid → OK | test_agents_fm_valid | PASS |
| Missing CODEX.md/GEMINI.md → warn only | test_missing_optional | PASS |
| Missing AGENTS.md/CLAUDE.md → error exit | test_missing_required | PASS |
| Drift report: YAML format correct | test_report_format | PASS |

Total: 8 PASS, 0 errors
