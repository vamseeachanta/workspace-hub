# WRK-1039 Plan — Codex perspective

## Assessment
Concur with Claude. Gap 1-14 detection layer complete. Three distinct remaining items.

## Steps
1. `exit_stage.py`: add `"pending/"` and `"working/"` to the queue-root path prefix tuple
   (currently only `"done/"` is handled). One-line change; high confidence.
2. `verify-gate-evidence.py` workstation display: introduce `_get_list_field(front, key)`
   helper (regex for multi-line list); use in details string of "Workstation contract gate".
   Gate logic (`has_nonempty_field`) is correct — only details formatting is wrong.
3. AC3 sweep: systematic run with exit-code table. Mark expected exit codes before running.

## Tests
- T31: unit test with list-style `plan_workstations:\n  - dev-primary` — details must show "dev-primary"
- T32: unit test mocking Stage 1 contract against a tmp pending/ file
- AC3 matrix documented in evidence/ac3-verification.md

## Additions vs Claude plan
- Explicitly scope `_get_list_field` as a new helper (not modifying `has_nonempty_field`)
- Note: T41 scope boundary confirmed; do not touch SKILL.md in this WRK
