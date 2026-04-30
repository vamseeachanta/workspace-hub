# Yaw Moment Sweep Closeout and Next Calculation Prep — 2026-04-30

## Current state

Issue #2564 is complete and closed: <https://github.com/vamseeachanta/workspace-hub/issues/2564>.

Implementation landed in `digitalmodel`:

- Commit: <https://github.com/vamseeachanta/digitalmodel/commit/0db57cd564720431213ee659cb1787a55683e922>
- Primary module: `src/digitalmodel/naval_architecture/yaw_moment.py`
- Packaged example input: `src/digitalmodel/naval_architecture/data/yaw_moment_typical_ship.yml`
- Tests: `tests/naval_architecture/test_yaw_moment_sweep.py`
- User-facing docs: `docs/domains/marine-engineering/yaw-moment-sweep.md`

Validation evidence from `/mnt/local-analysis/digitalmodel-issue2564`:

| Gate | Evidence |
|---|---|
| Yaw sweep tests | `UV_NO_SYNC=1 uv run pytest tests/naval_architecture/test_yaw_moment_sweep.py -q` → 21 passed |
| Targeted regression | `UV_NO_SYNC=1 uv run pytest tests/naval_architecture/test_maneuverability.py tests/naval_architecture/test_yaw_moment_sweep.py -q` → 43 passed |
| Lint | `UV_NO_SYNC=1 uv run --with ruff ruff check src/digitalmodel/naval_architecture/yaw_moment.py tests/naval_architecture/test_yaw_moment_sweep.py src/digitalmodel/naval_architecture/__init__.py` → passed |
| Smoke generation | 35 rows, CSV/JSON tables, citation sidecar, artifact manifest, and four charts generated |
| Review | Initial Hermes review found MAJOR package-data/chart-contract issues; fixes applied; follow-up review verdict APPROVE |

## What the yaw-moment calculation now supports

The new calculation evaluates preliminary rudder-induced yaw moment over a speed/angle grid using:

```text
M_z = x_rudder_from_cg_m * transverse_force_N

The workflow now has a reusable pattern for future calculations:

1. Packaged typical input YAML under `src/digitalmodel/naval_architecture/data/`.
2. Dataclass-style parsed input surface.
3. Explicit unit conversion and sign convention fields.
4. CSV/JSON output tables with units.
5. Citation sidecar for engineering provenance.
6. Artifact manifest.
7. Required chart list and chart writers.
8. Wheel/package-data tests that protect both new and existing package resources.

## Recommended next calculation

Recommended next calculation: **rudder stock / steering gear torque sweep**.

Why this is the best next step:

- It reuses the same speed/rudder-angle sweep and rudder force basis from #2564.
- It adds a practical design output that follows directly from `scalar_normal_force_N`.
- It is bounded enough for one plan-gated T2 issue.
- It avoids jumping prematurely to full MMG/turning-circle simulation, which needs additional hydrodynamic derivatives and validation data.

Preliminary formula boundary for the next issue:

```text
T_rudder_stock = scalar_normal_force_N * stock_to_center_of_pressure_arm_m

The plan should clearly distinguish this as a preliminary steering/rudder-stock torque estimate, not a full steering gear machinery design calculation.

## Candidate next calculations

| Option | Calculation | Scope | Complexity | Recommendation |
|---|---|---:|---:|---|
| A | Rudder stock / steering gear torque sweep | Add torque vs speed/angle using rudder normal force and center-of-pressure arm | T2 | Best next |
| B | Turning-circle / Nomoto response estimate | Uses yaw moment plus vessel yaw inertia and Nomoto `K`, `T` or derivatives | T3 | Good after torque sweep or when coefficients are available |
| C | Environmental yaw moment envelope | Wind/current yaw moments using OCIMF/OrcaFlex-style coefficients | T2/T3 | Good if current/wind design envelopes are the next business need |
| D | Calm-water resistance / power-speed curve | Hull resistance, effective power, delivered power | T2/T3 | Useful but separate stream from rudder/yaw workflow |

## GitHub-ready issue draft for recommended next calculation

Suggested title:

```text
feat(naval-arch): rudder stock torque sweep input for typical ship

Suggested labels:

```text
enhancement, priority:medium, cat:engineering-calculations, domain:naval-architecture, domain:hydrodynamics

Suggested body:

```markdown
## Summary
Build a plan-gated rudder stock / steering gear torque sweep for a typical ship, reusing the #2564 yaw-moment input pattern and rudder force calculation surface.

## Motivation
#2564 now produces rudder force and yaw moment over forward speed and rudder-angle grids. The next practical design calculation is the rudder stock torque envelope, which converts scalar rudder normal force into a torque demand using a center-of-pressure / stock-offset lever arm.

## Scope
- Add or extend a typical-ship YAML input with rudder stock / center-of-pressure geometry.
- Compute preliminary rudder stock torque across speed and rudder-angle sweeps.
- Produce CSV/JSON tables with units and sign/force convention fields.
- Produce required charts, likely:
  - torque vs rudder angle by speed
  - torque vs speed by rudder angle
  - scalar normal force vs rudder angle by speed
  - speed/angle torque heatmap
- Emit citation/provenance sidecar and artifact manifest.
- Add TDD coverage for formula, units, packaging, outputs, and charts.

## Scope boundaries
- In scope: preliminary force × lever-arm torque envelope.
- Out of scope: full steering gear machinery sizing, structural rudder-stock stress checks, bearing reactions, classification-rule scantlings, hydraulic actuator sizing, and full MMG maneuvering simulation.

## Starting evidence
- #2564 completed yaw moment sweep: https://github.com/vamseeachanta/workspace-hub/issues/2564
- `digitalmodel` commit: https://github.com/vamseeachanta/digitalmodel/commit/0db57cd564720431213ee659cb1787a55683e922
- Existing rudder force helper: `digitalmodel/src/digitalmodel/naval_architecture/maneuverability.py`
- New yaw-moment implementation surface: `digitalmodel/src/digitalmodel/naval_architecture/yaw_moment.py`

## Workflow
Engineering-critical calculation. Follow issue → resource intelligence → plan → adversarial review → user approval → TDD implementation → cross-review → close.

## Next-session copy/paste prompt

Use this if starting fresh:

```text
We completed #2564 yaw moment sweep. Start the next plan-gated engineering calculation: rudder stock / steering gear torque sweep for a typical ship. Load engineering-issue-workflow and issue-planning-mode. Use #2564 and digitalmodel commit 0db57cd564720431213ee659cb1787a55683e922 as resource-intelligence anchors. Create or update a GitHub issue as needed, draft the canonical workspace-hub plan under docs/plans/, run adversarial plan review, and stop at status:plan-review for my approval before implementation.

## Operator checklist before starting the next calculation

1. Confirm the selected next calculation with the user if they do not explicitly choose option A/B/C/D.
2. Search GitHub for duplicates before creating a new issue.
3. Re-read #2564 closeout evidence and `digitalmodel` commit `0db57cd564720431213ee659cb1787a55683e922`.
4. Run resource intelligence for the selected calculation, including `/mnt/ace` and naval-architecture wiki references when engineering standards or textbook context is needed.
5. Draft a canonical plan in `workspace-hub/docs/plans/`.
6. Run adversarial plan review.
7. Apply `status:plan-review` and stop for user approval before coding.
