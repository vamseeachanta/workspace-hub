Further tightened #2269 after wave-2 blockers.

This patch wave explicitly closes more of the remaining Codex/Gemini concerns:
- permanent two-path bootstrap policy is now stated explicitly
- exact `verification_method` string contract is now pinned
- YAML schema now includes a concrete `tutorials` example and typed field constraints
- dependency injection for bootstrap-path tests is explicit via `OPENFOAM_BASHRC_PATHS`
- benchmark trigger is exact: `--benchmark pitzDaily`
- `damBreak` is now explicitly runner-internal / outside canonical baseline acceptance unless promoted later
- reproducibility instructions for the cavity manifest are more concrete

Launching another current-text rereview wave on the patched plan now.
