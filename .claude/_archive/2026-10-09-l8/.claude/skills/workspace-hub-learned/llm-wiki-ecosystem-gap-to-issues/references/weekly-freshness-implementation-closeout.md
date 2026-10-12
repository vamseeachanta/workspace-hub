# Weekly freshness implementation closeout pattern

Use after a weekly-cadence LLM-wiki issue moves from approved plan to implementation.

## Durable implementation shape

A useful weekly freshness control loop should leave these durable artifacts, not just a narrative report:

1. A deterministic generator script for the weekly freshness/control-loop report.
2. A deterministic validator script for the generated report and machine-readable summary.
3. A concept/source watchlist file under `data/` that future weeks can update without editing code.
4. An issue-routing map under `data/` so stale concepts can become actionable GitHub work rather than passive observations.
5. A dated human-readable report under `docs/reports/`.
6. A dated machine-readable summary under `artifacts/freshness/`.
7. Focused tests for the generator, validator, watchlist parsing, stale/missing concept detection, and routing behavior.
8. README or command documentation showing the exact generation and validation commands.

## Validation closeout checklist

Before closing the implementation issue:

- Run the targeted regression tests affected by public-safety / wiki-safety changes.
- Run the targeted weekly freshness tests.
- Run the generator and validator together; require an explicit `OK`/success result.
- Run the full test suite if the repo size permits it.
- Run final adversarial code review after the implementation and test results are available.
- Post a closeout comment with the commit, pushed branch state, test evidence, generated artifacts, and final review disposition.
- Verify `main...origin/main` is clean/synced before closing the issue.

## Pitfalls

- Do not let weekly freshness become a hand-written status memo. The value is repeatability: data files + scripts + tests + generated outputs.
- Do not close on generator success alone; validators and tests must prove the produced report shape is stable.
- Do not bury routing decisions in prose. Keep concept-to-issue routing computable so the next weekly run can drive planning work.
- Do not skip adversarial re-review after implementation; plan-review approval does not replace code-stage review.
