# WRK-1042 AC Test Matrix

| AC | Test | Result |
|----|------|--------|
| tidy reads .wrk-id sentinel when dir name does not match wrk-NNN-slug | T13 (dry-run detect) + T13b (live delete) | PASS |
| spawn-team.sh recipe includes sentinel write | T11b (.wrk-id line in recipe) | PASS |
| existing tests still pass | T1-T12 | PASS (17/17) |
| non-conforming dir with sentinel + archived WRK → deleted | T13b | PASS |
| non-conforming dir with sentinel + non-archived WRK → preserved | T14 | PASS |
