# WRK-1039 Plan — Claude perspective

## Assessment
Implementation (Gap 1-14) already shipped in WRK-1035. WRK-1044 added D-layer prevention.
Remaining: 3 targeted fixes + AC3 verification.

## Steps
1. Fix `exit_stage.py` path resolution: extend `done/` queue-root logic to `pending/`/`working/`
2. Fix `verify-gate-evidence.py` workstation details: replace `get_field()` (scalar-only) with
   a helper that also reads list-style YAML for the details string (gate logic correct, display wrong)
3. AC3 sweep: run verifier against 10 audit WRKs + WRK-1044/1047 regression; document exit codes

## Tests
- T31: workstation list-style YAML renders value not "missing" in details
- T32: exit_stage.py Stage 1 exit passes with pending/ path
- AC3-sweep: table of 12 WRKs with expected vs actual exit codes

## Risk
- Low. All changes are display/path fixes; no gate logic altered.
- T41 (SKILL.md 260 lines) is WRK-1044's debt — excluded from this WRK's scope.
