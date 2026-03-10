# WRK-1099 AC Test Matrix

| # | Acceptance Criterion | Test | Result |
|---|----------------------|------|--------|
| 1 | `--subcategory <name>` filters by matching subcategory | test_whats_next.bats:1 | PASS |
| 2 | `--subcategory` + `--category` AND filter | test_whats_next.bats:2 | PASS |
| 3 | `--subcategory` without `--category` filters across all categories | test_whats_next.bats:3 | PASS |
| 4 | Current-machine items before other-machine items per section | test_whats_next.bats:4 | PASS |
| 5 | `[this machine: <hostname>]` sub-header when mixed | test_whats_next.bats:5 | PASS |
| 6 | `[other machines: WRK-X …]` brief one-liner for remote | test_whats_next.bats:6 | PASS |
| 7 | Existing flags (`--all`, `--category`, `--limit`) unchanged | manual verify | PASS |

All 6 bats tests PASS. 0 FAIL.
