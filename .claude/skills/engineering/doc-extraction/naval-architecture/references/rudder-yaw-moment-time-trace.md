# Rudder yaw-moment and time-trace workflow notes

Use these notes when a user asks for rudder-induced yaw moment sweeps, vessel-specific rudder input files, turning-circle/time-trace estimates, or project-specific benchmark reports.

## Source-intelligence pattern

1. If the data lives in a project repo that may be syncing or sparse-checked-out, verify sync state first:
   - check for active sync/git processes,
   - check `git rev-list --left-right --count HEAD...@{u}` when local repo exists,
   - verify the required project path is materialized locally.
2. If the repo is current but the project path is missing because of sparse checkout, use GitHub API/raw downloads as the source of record and record that local path is sparse.
3. Before implementation, create/update an LLM-wiki project/domain page set with:
   - vessel/project aliases,
   - source file paths,
   - extracted geometry/constants with units,
   - uncertainty/status classification,
   - downstream calculation boundaries.
4. Create a source-pack/benchmark issue before calculation issues when source evidence is scattered across workbook, converted script, notes, and PDFs.

## B1528/SIROCCO example facts captured from session

Source repo: `vamseeachanta/acma-projects`, project path `B1528`.

Important source paths:
- `B1528/excel_to_py/Rudder Force & Yaw Moments.xlsx`
- `B1528/excel_to_py/rudder_force_yaw_moment.py`
- `B1528/ref/SIROCCO breakaway notes.docx`
- `B1528/ref/ECDIS Mar 26 Midnight LT.docx`
- `B1528/excel_to_py/27. SIROCCO-000272-GA Plan.pdf`

Initial extracted values:
- Vessel/source spelling: `SIROCCO`; user spelling `Sorrocco` is an alias.
- `LBP = 225.5 m`.
- Rudder area: `44.9395631937 m^2`.
- Rudder center aft of AP: `-1.0520261379 m`.
- Legacy workbook yaw lever: `0.6 * LBP = 135.3 m`; do **not** silently equate this to `x_rudder_from_cg_m` without mapping evidence.
- Workbook constant/factors seen: `beta = 600`, `Cr = 1.065 / 0.935`.
- Requested operating point in that session: forward speed `2.5 kn`, rudder `+1 deg` and `-1 deg`.
- Preliminary workbook-family hand checks at `2.5 kn`:
  - `+1 deg`, `Cr=1.065`: approximately `+112.143 kN-m` (`+11.435 mt-m`).
  - `-1 deg`, `Cr=0.935`: approximately `-98.454 kN-m` (`-10.040 mt-m`).
  Treat these as regression targets for workbook mode only until formula/sign/lever semantics are proven.

## Model-boundary rules

- Separate `workbook_regression` outputs from reusable `digitalmodel_static_yaw` outputs. Do not blend constants or label them as the same method.
- If using an existing static yaw-moment API, document how the project lever arm maps into `x_rudder_from_cg_m`; AP-based or `0.6*LBP` workbook arms are not automatically CG arms.
- For time traces, avoid double-counting:
  - A first-order Nomoto model can govern state update: `r_dot = (K * alpha_R - r) / T`.
  - Rudder force and yaw moment computed from local inflow should be diagnostics only in that mode unless a separately approved moment-balance model with inertia/damping replaces Nomoto `K/T`.
- Rudder-local inflow feedback terms for the preliminary Nomoto mode:
  - `v_R = x_R * r`
  - `beta_R = atan2(-x_R * r, U)`
  - `alpha_R = delta_cmd - beta_R`
  - `U_R = hypot(U, v_R)`
  - `psi_dot = r`, `x_dot = U*cos(psi)`, `y_dot = U*sin(psi)`.
- If project-specific `K/T` or benchmark track points are unavailable, report sensitivity/source-gap results rather than inventing calibration.

## Reporting requirements

For engineering-facing reports with interactive charts:
- include source path, unit, and status/provenance for every input value;
- include explicit sign convention and positive-yaw definition;
- include static charts such as yaw moment vs rudder angle by speed and yaw moment vs speed by rudder angle;
- include time-history charts such as trajectory, heading, yaw rate, effective rudder angle, local rudder speed, and yaw moment;
- label benchmark overlays with uncertainty and degrade to a source-gap panel if the benchmark is narrative-only;
- avoid IMO/class compliance, full MMG, or incident-causation claims unless separately scoped and supported.
