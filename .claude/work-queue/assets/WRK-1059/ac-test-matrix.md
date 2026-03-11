# WRK-1059 AC Test Matrix

| AC | Description | Test | Result |
|----|-------------|------|--------|
| 1 | Public symbol audit across all 5 repos | T19: --api → api: line present | PASS |
| 2 | Per-repo API docstring coverage % reported | run_api_audit() JSON parsing | PASS |
| 3 | docs/ structure validated; missing files listed | T15–T18: docs-index/changelog/build checks | PASS |
| 4 | Codex cross-review passes | submit-to-codex.sh → Verdict: APPROVE | PASS |

## Test Run
```
bash tests/quality/test_check_all.sh
Results: 35 passed, 0 failed

uv run --no-project python -m pytest tests/quality/test_api_audit.py -q
12 passed in 0.14s
```
