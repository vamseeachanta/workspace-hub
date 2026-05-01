# B1528 SIROCCO yaw-moment / time-trace exit handoff — 2026-05-01

## Executive status

B1528 execution wave is complete for the project-specific source pack, static yaw-moment report, and time-trace benchmark report.

| Issue | State | Terminal label | Result |
|---|---:|---|---|
| #2569 | CLOSED | `status:done` | B1528 SIROCCO source pack and benchmark extraction completed. |
| #2570 | CLOSED | `status:done` | Static yaw-moment input/report completed and published to `digitalmodel` `main`. |
| #2571 | CLOSED | `status:done` | Time-trace benchmark report with rudder-local inflow feedback completed and published to `digitalmodel` `main`. |

`digitalmodel` `main` verification from GitHub API:

- HEAD at verification time: `9008e102ff98d5465ef043c7f7466edb76e28668`
- HEAD message: `feat: add B1528 SIROCCO time-trace report for issue 2571`
- HEAD date: `2026-05-01T09:46:40Z`

Local `git status`/worktree commands in `workspace-hub` and nested `digitalmodel` repeatedly timed out during the session, so final publication and verification used GitHub Contents/API against `main`.

## Published digitalmodel artifacts

### #2570 static yaw-moment report

Verified on `vamseeachanta/digitalmodel@main`:

- `src/digitalmodel/naval_architecture/b1528_sirocco_yaw_report.py`
- `src/digitalmodel/naval_architecture/data/b1528_sirocco_yaw_moment.yml`
- `tests/naval_architecture/test_b1528_sirocco_yaw_moment.py`
- `docs/domains/marine-engineering/b1528-sirocco-yaw-moment-report.md`
- `outputs/b1528_sirocco/b1528_sirocco_yaw_moment_report.html`
- generated CSV/JSON/provenance/Markdown/manifest under `outputs/b1528_sirocco/`
- `scripts/review/results/2026-05-01-implementation-2570-hermes.md`

Key workbook-regression operating points at `2.5 kn`:

| Case | Result |
|---|---:|
| `+1 deg`, port `Cr=1.065` | `+112.158527 kN-m` |
| `-1 deg`, stbd `Cr=0.935` | `-98.467815 kN-m` |

Validation evidence:

- Targeted pytest: `6 passed in 36.90s`.
- Ruff: `All checks passed!`.
- Smoke generation: `84` rows plus CSV/JSON/provenance/Markdown/HTML/manifest.
- Review: `APPROVE` after MINOR caveat-consistency fix.

Scope caveat: static rudder-induced yaw moment only; not a full MMG simulation, incident reconstruction, IMO compliance assessment, or class compliance conclusion.

### #2571 time-trace report

Verified on `vamseeachanta/digitalmodel@main`:

- `src/digitalmodel/naval_architecture/b1528_sirocco_time_trace.py`
- `src/digitalmodel/naval_architecture/data/b1528_sirocco_time_trace.yml`
- `tests/naval_architecture/test_b1528_sirocco_time_trace.py`
- `docs/domains/marine-engineering/b1528-sirocco-time-trace-report.md`
- `outputs/b1528_sirocco/time_trace/b1528_sirocco_time_trace_report.html`
- generated CSV/JSON/provenance/Markdown/manifest under `outputs/b1528_sirocco/time_trace/`
- `scripts/review/results/2026-05-01-implementation-2571-hermes.md`

Implemented governing model:

```text
v_R = x_R * r
beta_R = atan2(-x_R * r, U)
alpha_R = delta_cmd - beta_R
U_R = hypot(U, v_R)
r_dot = (K * alpha_R - r) / T
psi_dot = r
x_dot = U * cos(psi)
y_dot = U * sin(psi)
```

Important model boundary: rudder force and yaw moment are diagnostics only and are **not** fed back into `r_dot`, avoiding double-counting direct moment balance and Nomoto `K/T` response.

Smoke generation:

- `3` scenarios: positive rudder, negative rudder, zero rudder.
- `1803` time-history rows.
- Interactive Plotly charts for trajectory, heading, yaw rate, effective rudder angle, diagnostic yaw moment, and benchmark source-gap panel.

Validation evidence:

- Targeted pytest initially passed: `7 passed in 15.73s`.
- Ruff: `All checks passed!`.
- Smoke generation passed: `3` runs / `1803` rows.
- Review artifact verdict: `APPROVE with documented environment caveat`.

Environment caveat: later pytest reruns timed out after successful validation; no code changes occurred after the passing pytest/ruff gates except documentation text. Treat this as a local runner/uv environment caveat, not a known numerical failure.

## Source / benchmark boundary

#2569 source-pack evidence is narrative benchmark context, not an instrumented validation dataset:

- B1528 canonical spelling: `SIROCCO`; alias captured: `Sorrocco`.
- `LBP = 225.5 m`.
- `rudder_area = 44.93956319369854 m²`.
- legacy workbook yaw lever: `0.6 * LBP = 135.3 m`.
- workbook-regression note: workbook text mentions `Ft`, but evaluated yaw moment uses `Fn` through the workbook cell family.
- VDR/Rosepoint evidence contains heading/SOG narrative anchors but no x/y coordinate trajectory and includes tug/current/anchor/bank effects.

Therefore #2571 intentionally emits a `benchmark-source-gap` panel rather than fabricating a quantitative overlay.

## Remaining approved but unfinished work

The B1528 issue trio is done. Separate previously approved naval-architecture expansion issues remain open:

| Issue | State | Label | Title |
|---|---:|---|---|
| #2566 | OPEN | `status:plan-approved` | Full CI and package validation for yaw and rudder-stock sweep workflows |
| #2567 | OPEN | `status:plan-approved` | Standards-backed steering gear and rudder-stock design checks |
| #2568 | OPEN | `status:plan-approved` | Preliminary turning-circle and tactical-diameter estimator input workflow |

Recommended next wave after exit: execute #2566 first as a quality/packaging gate, then #2568 if the user wants reusable turning metrics generalized beyond B1528, then #2567 standards-backed decomposition.

## Fresh-session copy/paste prompt

```text
Resume from the B1528 SIROCCO exit handoff:
/mnt/local-analysis/workspace-hub/docs/session-handoffs/2026-05-01-b1528-yaw-moment-time-trace-exit-handoff.md

Do not redo #2569/#2570/#2571 unless verification finds a real remote regression. They are closed with status:done and their artifacts are published to vamseeachanta/digitalmodel@main. First verify remote issue/file state via GitHub API because local git status/worktree commands have timed out in workspace-hub and nested digitalmodel.

If continuing naval-architecture work, the remaining approved issues are #2566, #2567, #2568. Recommended order: #2566 quality/package validation, then #2568 reusable turning estimator, then #2567 standards-backed steering/rudder-stock decomposition. Follow plan-approved issue execution workflow, TDD, validation, adversarial review, API publishing if local git remains unreliable, and closeout comments before closing issues.
```

## Exit checklist

- [x] B1528 source pack issue #2569 closed.
- [x] Static yaw-moment issue #2570 closed.
- [x] Time-trace issue #2571 closed.
- [x] Remote `digitalmodel@main` artifact existence verified via GitHub API.
- [x] Workspace-hub plan/index updates for #2570/#2571 published.
- [x] Handoff written for next session.
- [ ] Optional next session: investigate local git status/worktree hangs before broad local-merge work.
