# WRK-1090 Test Results

## Suite: tests/quality/test_dep_health.sh

```
Results: 11 passed, 0 failed
```

Commit: 7c2e4c48

| Test | Scenario | Result |
|------|----------|--------|
| T1 | freshness stale → exit 1 | PASS |
| T1b | STALE in output | PASS |
| T2 | fresh lock → exit 0 | PASS |
| T3 | outdated → exit 0 (warn only) | PASS |
| T3b | WARN in output | PASS |
| T4 | CVE vuln → exit 1 | PASS |
| T4b | BLOCKING in output | PASS |
| T5 | clean CVE scan → exit 0 | PASS |
| T6 | auto-WRK file created | PASS |
| T7 | YAML report created | PASS |
| T7b | run_at field present | PASS |
