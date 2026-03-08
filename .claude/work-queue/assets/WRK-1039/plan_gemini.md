# WRK-1039 Plan — Gemini perspective

## Assessment
Concur. The three items are orthogonal and low-risk. Recommend same order as Claude/Codex
(path fix → display fix → verification sweep) since path fix is already done and validates
the approach before touching verify-gate-evidence.py.

## Steps
1. `exit_stage.py` path fix (done): confirm test passes — `Stage 1 exit validated` for WRK-1039.
2. `verify-gate-evidence.py` workstation display: add `_get_list_field` helper; update details
   f-string in "Workstation contract gate" block only. No changes to `has_nonempty_field`.
3. AC3 sweep: run all 12 WRKs, capture exit codes, verify --json mode outputs valid JSON.
   Expected: 7 exit-1 (fabricated), 5 exit-0 (legitimate); document any surprises.

## Tests
- T31 + T32 as described by Codex.
- Suggest adding T33: `--json` mode on a known-failing WRK returns `{"pass": false}` not error.

## Synthesis note
All three provider plans agree. No conflicts. Recommend proceeding with unified plan.
