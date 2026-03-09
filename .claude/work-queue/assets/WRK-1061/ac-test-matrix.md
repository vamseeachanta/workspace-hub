# WRK-1061 AC Test Matrix

| # | Acceptance Criterion | Test | Result |
|---|---------------------|------|--------|
| 1 | `generate-review-input.sh WRK-NNN` produces a valid input file | Test 1, 7, 8, 9, 10 | PASS |
| 2 | Output includes: mission, ACs, diff, test snapshot, focus prompts | Test 2, 8, 9, 10 | PASS |
| 3 | Diff truncation works for >300 line diffs | Test 4 | PASS |
| 4 | `--phase N` flag included in output filename | Test 3 | PASS |
| 5 | Integrates with `cross-review.sh` without modification | Smoke test (direct file path) | PASS |
| 6 | Cross-review (Codex) passes | Pending Stage 13 | PENDING |

**Test run:** `bash tests/testing/test-generate-review-input.sh`
**Result:** 10/10 PASS, 0 FAIL
