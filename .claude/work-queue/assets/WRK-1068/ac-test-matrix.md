# WRK-1068 AC Test Matrix

| # | Acceptance Criterion | Test(s) | Result |
|---|---------------------|---------|--------|
| 1 | dep-graph.py reads all pending + working WRK items | `test_empty_graph_*`, live run against 490-item queue | PASS |
| 2 | ASCII critical-path table output | `test_single_chain_critical_path`, `test_diamond_dependency` | PASS |
| 3 | DOT file output for optional SVG rendering | format_dot tested inline, `--dot` flag implemented | PASS |
| 4 | `--category` and `--critical-path` filter flags work | `test_category_filter_*` (2 tests) | PASS |
| 5 | `/work list` footer shows unblocked count + longest chain | `test_format_summary_*`, live `work.sh --provider claude list` | PASS |
| 6 | Cross-review (Codex) passes | Codex REQUEST_CHANGES resolved; 4 MAJOR findings addressed | PASS |

## Test Run Summary
- Total: 14 tests
- Passed: 14
- Failed: 0
- Command: `uv run --no-project python -m pytest scripts/work-queue/tests/test_dep_graph.py -v`
