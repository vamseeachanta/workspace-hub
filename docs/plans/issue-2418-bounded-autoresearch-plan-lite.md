# Bounded autoresearch iterations

The bounded slice of issue 2418 will extend the existing runner with opt-in repeated attempts and stopping bounds.

## Plan-lite

- Scope: `scripts/skills/repo_ecosystem_autoresearch.py` will accept an iteration
  count, defaulting to one, and retain the existing elapsed-budget default.
- Controller: repeated calls to the existing attempt function will compound
  accepted content and restore the last accepted content after rejection.
  Attempt and elapsed limits will govern admission; plateau, regression,
  unavailable candidates and dry runs will stop iteration. The summary will
  expose attempted, kept and reverted counts and a stable stop reason.
- Tests: synthetic score tables and clocks will cover default and opt-in
  execution, acceptance, restoration, stopping boundaries, invalid arguments
  and CLI wiring. The existing runner regression cases will also run, using
  temporary fixtures without external candidate execution.
- Exclusions: durable cumulative reporting, cost telemetry, new evaluators,
  live candidate execution, scheduling changes and interruption of active
  callbacks will remain outside this slice. The elapsed budget will bound
  admission to subsequent attempts rather than interrupt an active callback.

## Verification

The local verification command will run both controller and runner suites:

```bash
uv run --offline --no-project --with pytest python -m pytest \
  tests/skills/test_autoresearch_iterations.py \
  tests/skills/test_repo_ecosystem_autoresearch.py \
  -q -rA -p no:cacheprovider --basetemp="$TMPDIR/autoresearch-tests"
```

A local pass will establish the synthetic controller and regression behavior
only. Hosted workflow failures will require separate diagnosis before merge.
