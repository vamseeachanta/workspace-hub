# AC Test Matrix — WRK-1039

| AC | Description | Test(s) | Result |
|----|-------------|---------|--------|
| AC1 | All 14 gaps from session-audit-master.md in verifier (done in WRK-1035) | T11-T30 | PASS |
| AC2 | Each fix has a corresponding test (T11-T30 + T1-T4 = 26 tests) | T11-T30, T1-T4 | PASS |
| AC3 | verify-gate-evidence.py exits 1 on fabricated audit WRKs | T33 + AC3 sweep | PASS (8/8 fabricated exit=1) |
| AC3b | verify-gate-evidence.py exits 0 on clean WRKs | AC3 sweep | PASS (WRK-1044 exit=0) |
| AC4 | verify-gate-evidence.py --json produces valid JSON with correct outcome field | T33 | PASS |
| AC5 | Workstation details display string no longer shows "missing" for list-style fields | T31 | PASS |
| AC6 | No regression in passing tests (T41 excluded — WRK-1044 scope, pre-existing) | full suite | PASS (115 pass) |
| AC7 | exit_stage.py pending/working/ path resolution bug fixed | T32 | PASS |

## Notes

- WRK-1034 and WRK-1036 exit=1 (not exit=0 as planned): both have real Gap detections
  (browser elapsed 0s, sentinel values, shared commits). These are correct detections.
- Two additional bugs fixed during AC3 sweep: DST timezone parsing, archive path staleness.
