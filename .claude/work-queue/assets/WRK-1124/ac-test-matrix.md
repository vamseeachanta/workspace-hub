# AC Test Matrix — WRK-1124

| Test | Type | Expected | Result |
|------|------|----------|--------|
| Pending item with checkpoint.yaml shows in UNCLAIMED | happy | WRK-1123 (Stage 3) and WRK-1109 (Stage 1) in UNCLAIMED section | PASS |
| Stage column: checkpoint item at hard gate shows WAITING | happy | WRK-1109 Stage 1 → STATUS=WAITING | PASS |
| Stage column: checkpoint item at non-gate shows START | happy | WRK-1123 Stage 3 → STATUS=START | PASS |
| Stage column: no checkpoint shows `—` and READY | happy | All MEDIUM items show `—` READY | PASS |
| PID column: WORKING row shows PID | happy | WRK-1069 → `PID 390229` in WORKING section | PASS |
| PID column: UNCLAIMED row shows PID | happy | WRK-1109 → `PID 3190592` in UNCLAIMED section | PASS |
| PID column: absent session-lock omits gracefully | edge | Items with no session-lock show `—` in PID column | PASS |
| Items in working/ unaffected | happy | WRK-1022, WRK-1069 remain in WORKING section | PASS |
| Pending items without checkpoint stay in MEDIUM | happy | All no-checkpoint pending items stay in MEDIUM | PASS |
| Bash syntax check | edge | `bash -n whats-next.sh` → syntax OK | PASS |
| BLOCKED section row parsing | edge | EXT_BLOCKED rows parse correctly with new 8-field format | PASS |
