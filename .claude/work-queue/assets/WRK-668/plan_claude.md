# WRK-668 Plan — Claude Review

## Assessment

The plan correctly identifies all 7 gaps from the WRK-624 gap review and addresses them
in the right dependency order. Key strengths:

1. **TDD-first sequence** — T1-T3 tests written RED before implementation; correct approach
   for gate check functions that are pure functions of YAML input
2. **Schema-first design** — defining `archive-tooling-template.yaml` before writing code
   ensures the validator and HTML card have a stable contract to target
3. **Spin-off script scoped correctly** — `create-spinoff-wrk.sh` takes source WRK + blocker
   description as inputs; avoids hardcoding blocker logic in the verifier
4. **Stage 20 evidence hardened** — promoting best-effort to hard gate closes a real silent-
   failure risk

Risk: `verify-gate-evidence.py` is ~2100 lines; adding `--phase archive` without careful
module scoping could widen the function surface. Mitigate by keeping `check_archive_readiness()`
as a standalone function in a new `gate_checks_archive.py` (similar to `gate_checks_extra.py`)
and importing it, rather than adding inline to the main file.

## Verdict: APPROVE_WITH_MINOR

Suggest splitting `check_archive_readiness()` into `gate_checks_archive.py` rather than
adding to the already-large verifier. Otherwise plan is sound and deliverables are clear.
