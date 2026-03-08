# WRK-1039 Plan Final

> Route B inline plan — confirmed by vamsee on 2026-03-08T21:10:00Z

## Plan (synthesised from 3 provider views)

1. Fix `exit_stage.py` `pending/`/`working/` path resolution (done)
2. Fix workstation display detail string in `verify-gate-evidence.py`
3. AC3 verification sweep: 10 audit WRKs + 2 regression WRKs, normal + `--json` modes

## Tests
T31 (workstation list display), T32 (exit_stage Stage 1 path), T33 (--json fail JSON),
AC3-sweep (12 WRKs, expected exit codes pre-declared)

confirmed_by: vamsee
confirmed_at: 2026-03-08T21:10:00Z
decision: passed
