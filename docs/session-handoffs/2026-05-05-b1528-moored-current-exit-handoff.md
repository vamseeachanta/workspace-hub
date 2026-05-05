# B1528 SIROCCO moored-current exit handoff — 2026-05-05

## Executive status

B1528 SIROCCO/Sorrocco moored-current rudder force-component reporting is
complete and ready for engineer review on 2026-05-06.

| Repository | Branch | Sync state | HEAD |
|---|---|---|---|
| `digitalmodel` | `main` | `origin/main...HEAD = 0 0` | `989e20eb test(#2568): TDD tests for turning-circle and tactical-diameter estimator` |
| `acma-projects` | `main` | `origin/main...HEAD = 0 0` | `105c9ce8 chore(B1528): add SIROCCO moored-current PDF report` |

The moored-current calculation package itself was added in `digitalmodel`
commit:

- https://github.com/vamseeachanta/digitalmodel/commit/bcb6a1614649

`digitalmodel` later advanced to `989e20eb` with turning-circle estimator tests;
that later commit is now also on `origin/main`.

## Completed issue

| Issue | State | Result |
|---|---:|---|
| [workspace-hub #2642](https://github.com/vamseeachanta/workspace-hub/issues/2642) | Closed, completed | B1528 SIROCCO moored-current rudder force components at COG for 3.5 kn current and +/-1 to +/-5 deg rudder. |

Completion comments were posted on #2642 with both the `digitalmodel` report
package and the `acma-projects` PDF links.

## Published report links

### digitalmodel

- Durable report: https://github.com/vamseeachanta/digitalmodel/blob/main/docs/domains/marine-engineering/b1528-sirocco-moored-current-report.md
- Generated HTML: https://github.com/vamseeachanta/digitalmodel/blob/main/outputs/b1528_sirocco/moored_current/b1528_sirocco_moored_current_report.html
- Generated Markdown: https://github.com/vamseeachanta/digitalmodel/blob/main/outputs/b1528_sirocco/moored_current/b1528_sirocco_moored_current_report.md
- Results CSV: https://github.com/vamseeachanta/digitalmodel/blob/main/outputs/b1528_sirocco/moored_current/b1528_sirocco_moored_current_results.csv
- Results JSON: https://github.com/vamseeachanta/digitalmodel/blob/main/outputs/b1528_sirocco/moored_current/b1528_sirocco_moored_current_results.json
- Master calculation review: https://github.com/vamseeachanta/digitalmodel/blob/main/docs/domains/marine-engineering/rudder-and-ship-force-calculation-review.md

### acma-projects

- PDF report: https://github.com/vamseeachanta/acma-projects/blob/main/B1528/output/b1528_sirocco_moored_current_report.pdf
- PDF commit: https://github.com/vamseeachanta/acma-projects/commit/105c9ce84d0862382f1efaabd60780dce41783a9
- Local PDF path: `/mnt/local-analysis/workspace-hub/acma-projects/B1528/output/b1528_sirocco_moored_current_report.pdf`

## Calculation scope

Scenario implemented:

- vessel condition: moored
- ship speed over ground: `0.0 kn`
- current passing rudder: `3.5 kn`
- rudder sweep: `1, 2, 3, 4, 5 deg` to port and starboard
- COG components reported: `X`, `Y`, `Z`, `K`, `M`, `N`
- propeller rotation factor: `Cr=1.0`

The report uses the B1528/Barrass workbook family:

```text
V = 3.5 kn * 0.51444
F = beta * A_R * V^2 * Cr
Fn = F * sin(delta)
X = F * sin(delta)^2
Y = F * sin(delta) * cos(delta)
N = Y * (0.6 * LBP)
```

Sign convention:

- `+X`: downstream/current-drag direction
- `+Y`: port
- `+Z`: upward
- `+N`: bow-to-port yaw moment
- `Z`, `K`, and `M`: zero in the bounded planar rudder-only model

`Cr=1.0` is used because this moored-current case excludes propeller-rotation
correction. It is the neutral no-amplification/no-reduction multiplier and does
not model locked/freewheeling propeller drag or wake effects.

## Sample check point

Generated sample point:

```text
Scenario: moored current, port rudder 1 deg
V = 3.5 kn * 0.51444 = 1.80054 m/s
F = 600 * 44.939563 * 1.80054^2 * 1.0 = 87414.936 N
Fn = F * sin(1 deg) = 1525.601 N
X = F * sin(1 deg)^2 = 26.625 N
Y = F * sin(1 deg) * cos(1 deg) = 1525.369 N
N = Y * 135.3 / 1000 = 206.382377 kN-m
```

The HTML report includes Plotly charts for sway force, yaw moment, surge drag,
horizontal resultant force, and the sample verification point.

## Verification performed

`digitalmodel`:

```text
PYTHONPATH=src UV_NO_SYNC=1 uv run python -m pytest \
  tests/naval_architecture/test_b1528_sirocco_yaw_moment.py \
  tests/naval_architecture/test_b1528_sirocco_time_trace.py \
  tests/naval_architecture/test_b1528_sirocco_moored_current.py
```

Result: `18 passed`.

Legal scan:

```text
scripts/legal/legal-sanity-scan.sh --repo=digitalmodel --diff-only
```

Result: `PASS`.

ACMA PDF metadata:

- 12 pages
- A4 landscape
- generated from `b1528_sirocco_moored_current_report.html`

## Known caveats

- Full `git status`/`git diff` on `acma-projects` can hang because of the large
  worktree. Prefer targeted checks or commit-specific verification.
- The moored-current report is rudder-induced only. Hull current loads,
  mooring-line stiffness, bank effects, tug loads, current-profile variation,
  propeller race, and class/IMO compliance conclusions remain excluded unless
  supporting coefficients or project requirements are supplied.
- `digitalmodel` `main` includes a later turning-circle test commit after the
  moored-current report commit. Do not assume `bcb6a161` is current HEAD; use it
  as the report-package commit and `989e20eb` as the verified current remote
  state at exit.

## Exit checklist

- [x] Moored-current issue #2642 created, documented, and closed.
- [x] `digitalmodel` report source, generated outputs, durable docs, tests, and
      master review update pushed.
- [x] ACMA PDF exported, committed, and pushed.
- [x] `acma-projects` synced with `origin/main`.
- [x] Handoff written for next session.
