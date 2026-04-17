### Verdict: MAJOR

### Summary
The plan is well-scoped and anchored in a proven reference implementation (#2070), with a sensible extraction of shared helpers across 8 cadence crons. However, the status-band boundary logic is inconsistent between pseudocode and the test list, several acceptance criteria lack measurable verification, and the shared-library fan-out risk is under-mitigated given the single-commit blast radius across 8 cadences.

### Issues Found
- [P1] Boundary inconsistency in compute_status_band: pseudocode uses strict `>` for both thresholds (so value == warn → GREEN, value == block → YELLOW), but test_compute_status_band_yellow specifies `warn < value ≤ block → YELLOW` (so value == block → YELLOW). Test and implementation disagree at the block boundary; also test_compute_status_band_green `value < warn` leaves value == warn under-specified. Clarify inclusivity on both edges and align tests with code.
- [P1] Missing test for the weekly scheduler-health script living under `worldenergydata/scripts/cron/` — the shared helper lives in workspace-hub, so the cross-repo sourcing path is unspecified. How does wed#309's script consume `scripts/cron/lib/cadence-common.sh` that lives in a different repository? No vendoring, symlink, or packaging strategy is described.
- [P2] Cron collision risk / host assumption: 4 quarterly jobs land on the same day with 1-hour gaps and 2 weekly jobs run simultaneously at `0 6 * * 1`. Plan does not state whether these run on one host, nor whether concurrent report generation competes for resources (git, disk, rate-limited APIs).
- [P2] Acceptance criterion 'Adversarial review ... overall PASS or revisions applied' is not binary — what constitutes PASS when 3 providers disagree? The Adversarial Review Summary table is still pending, so the plan cannot actually satisfy its own gate at review time.
- [P2] Shared-library blast radius: the plan acknowledges 'if the helper has a bug, all 8 break' but the mitigation ('re-running all 8 cadence tests') is a process promise, not a mechanism. No CI gate, no version pinning, no smoke-test runner is specified.
- [P2] `scripts/cron/state-size-report.sh` is explicitly excluded from refactor 'until a separate cleanup commit at end of cadence wave' — this forks the convention for the duration of the work and risks the cleanup never happening. No issue/owner is assigned for that cleanup.
- [P3] `cadence_period` uses `date` without timezone pinning. Crons running near midnight UTC vs local time could generate off-by-one period labels (e.g., `2026-W16` vs `2026-W17`).
- [P3] `compute_status_band` uses bash arithmetic `(( value > block ))` which fails silently on non-integer metrics (floats, strings like '12.5MB'). Reference cron #2070 may produce such values; not specified whether helpers handle only integers.
- [P3] Report-file naming `<name>-YYYY-MM.md` collides with weekly `<name>-YYYY-Www.md` only by suffix — fine, but `docs/reports/` growth is flagged as Open with no retention policy or cleanup cron defined.
- [P3] `tests/cron/test_cadence_common.sh` is listed as 'bats or pytest' — the choice should be made now since test infrastructure varies (bats needs installation; pytest needs shell-call harness). Existing `tests/cron/` convention not stated.

### Suggestions
- Pin `compute_status_band` semantics explicitly: document whether thresholds are inclusive-warn/exclusive-block or vice versa, then update both pseudocode and the three band tests to match. Add a boundary test at exactly `value == warn` and `value == block`.
- Resolve the cross-repo helper question for wed#309 up front: either (a) vendor the helper into worldenergydata, (b) symlink via a known mount, or (c) copy with a sync check. Add an acceptance criterion to verify the chosen mechanism.
- Stagger cron times more aggressively or introduce a lightweight lock (`flock /tmp/cadence.lock`) to prevent simultaneous runs from thrashing the host.
- Define 'adversarial review PASS' concretely: e.g., no P1 issues across any provider, or unanimous APPROVE, or 2-of-3 with documented rebuttal for the dissent.
- Add a `scripts/cron/lib/smoke-test.sh` that sources the helpers and runs a no-op invocation of each of the 8 cadences; wire it into pre-commit or a guard script so any helper change forces the fan-out verification.
- Create an explicit follow-up issue (or checklist item with owner + deadline) for the #2070 retroactive refactor at the end of the wave to prevent convention drift.
- Pin timezone: set `TZ=UTC` at the top of `cadence-common.sh` or in the crontab wrapper so period labels are deterministic across hosts.
- State integer-only vs float support for status metrics, or replace `(( ))` with a portable numeric comparator (`awk 'BEGIN{exit !($1 > $2)}'`) if floats are possible.
- Pick one test framework (pytest, given the repo's `uv run` convention) and specify the shell-invocation harness pattern once, so all 8 per-cadence tests are copy-paste consistent.
- Add an acceptance criterion that `docs/reports/cadence-schedule.md` is generated (not hand-written) by a script sourcing the crontab template, so the index cannot drift from the actual schedule.

### Questions for Author
- At the boundary values (`value == warn`, `value == block`), which band should be emitted? The pseudocode and tests disagree.
- How will `worldenergydata/scripts/cron/scheduler-health.sh` (wed#309) source `scripts/cron/lib/cadence-common.sh` from workspace-hub? Vendoring, symlink, or copy-with-sync?
- Are all 8 cadences intended to run on the same host? If so, is simultaneous execution at `0 6 * * 1` (two weeklies) acceptable, and what's the contention model for quarterlies stacked on Jan/Apr/Jul/Oct 1?
- What concretely defines an 'overall PASS' from the 3-provider adversarial review — unanimity, majority, or severity-weighted?
- Is the end-of-wave refactor of `state-size-report.sh` to use the shared helpers tracked as a concrete issue with an owner, or is it an aspirational footnote?
- Should metrics be integer-only, or do any of the 8 cadences need float/string comparisons (e.g., sizes in MB, percentages)?
- Which test framework — bats or pytest — and why? Does `tests/cron/` already have a convention?
- What's the retention/rotation policy for `docs/reports/<name>-<period>.md` files, given 8 cadences × multiple years will accumulate hundreds of files?
