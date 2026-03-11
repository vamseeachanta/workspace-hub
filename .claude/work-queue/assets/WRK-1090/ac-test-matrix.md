# WRK-1090 AC Test Matrix

| AC | Description | Test | Result |
|----|-------------|------|--------|
| AC1 | `scripts/quality/dep-health.sh` exists and runs | T2 (fresh, exits 0) | PASS |
| AC2 | Exit code 0 = healthy, 1 = CVEs/stale | T1 (stale→1), T4 (CVE→1), T5 (clean→0) | PASS |
| AC3 | YAML report at `logs/quality/dep-health-{datetime}.yaml` | T7 | PASS |
| AC4 | CVE HIGH/CRITICAL → auto-WRK item in pending/ | T6 | PASS |
| AC5 | Nightly cron entry in `crontab-template.sh` | manual verify | PASS |
| AC6 | ≥5 TDD tests | 11 tests total | PASS |
| AC7 | Passes `check-all.sh` (ruff+mypy) — bash only, no Python src | N/A (bash script) | PASS |

## Test Run Summary

```
Results: 11 passed, 0 failed
Suite:   tests/quality/test_dep_health.sh
Commit:  bea4e91b
```

## AC Coverage

- T1: freshness stale → exit 1  ✓
- T2: freshness fresh → exit 0  ✓
- T3: outdated warn-only → exit 0  ✓
- T4: CVE HIGH → exit 1  ✓
- T5: CVE clean → exit 0  ✓
- T6: auto-WRK creation  ✓
- T7: YAML report format  ✓
- T8–T11: edge cases (all PASS)  ✓
