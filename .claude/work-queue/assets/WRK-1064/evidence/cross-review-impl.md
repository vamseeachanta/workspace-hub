# Cross-Review: WRK-1064 Implementation (Stage 13)
Verdict: MINOR

## Findings

- [MINOR] Bypass JSONL log susceptible to malformed records from adversarial ref names.
  In `scripts/hooks/pre-push.sh` lines 71-77, `FIRST_LOCAL_REF`, `FIRST_LOCAL_OID`,
  `FIRST_REMOTE_REF`, and `FIRST_REMOTE_OID` are interpolated directly into a printf
  format string that produces a JSON record. A ref name containing `"` or a literal
  newline will produce invalid JSONL, breaking downstream log parsers.
  Recommendation: Write the bypass record via `uv run --no-project python -c` using
  `json.dumps` for safe serialisation, or strip/escape `"` from each field before
  interpolation. Deferred — no remote in this workspace has non-standard ref names.

- [MINOR] OGManufacturing absent from coverage extraction dict in run-all-tests.sh.
  Present in REPO_CONFIGS and TIER1_REPOS so tests run, but the coverage results dict
  omits OGManufacturing, silently producing no coverage data for the ratchet.
  Recommendation: Add OGManufacturing to the coverage dict, or add an inline comment
  explaining the exclusion. Deferred — OGManufacturing has no coverage baseline yet;
  tracked as future work.

## Summary

All four MAJOR/MINOR findings from Stage 6 plan cross-review are correctly resolved:
new-branch zero-OID guard, submodule git-dir resolution, logs/hooks/ mkdir -p, and
JSONL schema. Two residual MINORs are deferred as noted above. No blockers.
