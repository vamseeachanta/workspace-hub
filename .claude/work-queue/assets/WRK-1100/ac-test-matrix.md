# WRK-1100 AC Test Matrix

| # | AC | Test | Result |
|---|-----|------|--------|
| 1 | whats-next.sh skips standing+cadence items | bash whats-next.sh \| grep -c WRK-235 == 0 | PASS |
| 2 | WRK-235 absent from output | bash whats-next.sh \| grep WRK-235 → no output | PASS |
| 3 | WRK-234 present (standing, no cadence) | bash whats-next.sh \| grep WRK-234 → output present | PASS |
| 4 | All other items unaffected | bash whats-next.sh exit code 0, no extra exclusions | PASS |

All 4 ACs: PASS
