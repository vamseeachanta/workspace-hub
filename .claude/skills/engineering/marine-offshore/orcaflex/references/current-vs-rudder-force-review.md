# Current vs Rudder Force Review Pattern

Use this reference when comparing hull current loads (OCIMF-style coefficients) against rudder-induced steering forces for OrcaFlex / marine operations force-balance reviews.

## Core distinction

Do not treat a rudder-force report as total current loading. Rudder force can be zero when `rudder_angle == heading_offset`, but hull current load is still present and may dominate surge, sway, and yaw.

## Recommended component breakdown

For each heading/rudder case, compute and display individual and resultant terms:

```text
Fx_current, Fy_current, N_current
Fx_rudder,  Fy_rudder,  N_rudder
Fx_total = Fx_current + Fx_rudder
Fy_total = Fy_current + Fy_rudder
N_total  = N_current  + N_rudder
R_current = hypot(Fx_current, Fy_current)
R_rudder  = hypot(Fx_rudder,  Fy_rudder)
R_total   = hypot(Fx_total,   Fy_total)
```

## OCIMF-style hull current force basis

Use the environmental-loading convention from the OCIMF-style module:

```text
q  = 0.5 * rho * V^2
Fx = q * frontal_area_current * CXc
Fy = q * lateral_area_current * CYc
Mz = q * lateral_area_current * LOA * CMc
```

Typical projected-area first cut for a monohull/vessel review:

```text
frontal_area_current = beam * draft
lateral_area_current = LBP_or_LOA * draft
```

Make coefficient provenance explicit. If using sample/interpolated OCIMF-style coefficients instead of vessel-specific extracted OCIMF coefficient tables, label the result as first-cut / screening-level rather than final certified loading.

## Digitalmodel inspection anchor

When the task is in `digitalmodel`, start by inspecting the existing implementation before deriving fresh equations. The current OCIMF-style force implementation has been observed at:

```text
src/digitalmodel/marine_ops/marine_engineering/environmental_loading/ocimf.py
EnvironmentalForces.calculate_current_forces(...)
EnvironmentalForces.calculate_total_forces(...)
EnvironmentalForces.plot_force_diagram(...)
```

Use those methods as the source of truth for sign convention, coefficient names, and existing wind/current totals before wiring report output. Then locate the report generator, rudder-force calculation, tests, and generated artifacts with targeted searches for `rudder`, `OCIMF`, `current force`, `resultant`, and the report artifact names. Do not skip this inspection just because the formulas are known; stale parallel calculations are a common source of report drift.

If a context-compressed session preserves an active todo list, restore that list first, then continue from the current in-progress inspection step rather than restarting the analysis.

## Rudder-force basis

For a simple rudder estimate at current speed:

```text
F = beta * A_R * V^2 * Cr
alpha = rudder_angle - heading_offset
Fn = F * sin(alpha)
X_local = F * sin(alpha)^2
Y_local = F * sin(alpha) * cos(alpha)
[X_ship, Y_ship] = rotate local-current-frame loads by heading offset
N_ship = Y_ship * yaw_lever
```

## Interpretation checklist

- Compare current resultant vs rudder resultant as a ratio, not just absolute loads.
- Compare current yaw vs rudder yaw; yaw dominance can differ from force dominance.
- At zero heading offset, symmetric OCIMF sway/yaw may be zero, making rudder yaw visible, while surge current load still dominates total horizontal force.
- At small nonzero headings, hull current sway/yaw can dominate rudder loads by orders of magnitude; state this plainly if supported by the numbers.
- Preserve sign convention for heading, sway, and yaw; show enough selected positive/negative cases to catch sign reversals.

## Output format for review

Prefer a compact table with columns:

```text
heading, rudder, Fx_current, Fy_current, N_current, R_current,
Fx_rudder, Fy_rudder, N_rudder, R_rudder,
Fx_total, Fy_total, N_total, R_total
```

Then provide a short engineering interpretation separating:

1. known basis and geometry,
2. coefficient/source assumptions,
3. individual force comparison,
4. resultant/yaw comparison,
5. caveats and recommended next validation step.

## Report artifact checklist

When turning this comparison into an HTML/PDF engineering review artifact, include enough provenance for the report to stand alone:

- scope banner distinguishing rudder-induced loads from total hull current loads,
- input data table: vessel length basis, yaw lever, rudder area/span, density, beta/Cr, current sweep, heading/rudder grid,
- at least one sample hand calculation with unit conversion and intermediate terms,
- individual and resultant force tables for current, rudder, and combined totals,
- plots for component forces and resultant/yaw envelopes,
- method/provenance section stating whether coefficients are vessel-specific OCIMF tables or screening/sample coefficients.

For PDF export of interactive HTML reports, prefer a browser/Playwright print path with explicit print CSS/page breaks and suppressed headers/footers. Verify the generated PDF, not just the HTML: page count, page size/orientation, absence of browser URL/date/page headers, expected text sections, and visual readability of key plots.

## Artifact coherency gate

Before marking a current-vs-rudder review complete, run a coherency check across source, YAML/provenance, Markdown, HTML, PDF, CSV, JSON, and manifest outputs. This catches the common failure mode where the calculation code was updated but the deliverable artifacts or limitations text still describe an older rudder-only scope.

Required checks:

- Regenerate every declared artifact after source or YAML wording changes; do not trust previously checked-in reports.
- Scan generated Markdown/HTML/PDF text for stale phrases such as `rudder-induced only`, `not a total current-load`, or `hull current loads are excluded` when hull current forces are now included.
- Assert provenance/limitations do not contradict the calculation. If OCIMF-inspired hull-current terms are used, the limitation should say they are screening/placeholder/not vessel-specific coefficients, not that hull current loads are excluded.
- Verify manifest entries point to files that exist and include any newly generated PDF/static artifacts.
- Smoke-test HTML in a browser: page loads without console errors, Plotly charts render, dropdowns/selectors change the displayed case, and required chart/table IDs exist.
- Extract PDF text and check for the report title, OCIMF caveat, and the static current/rudder/total comparison sections; PDF generation success alone is not enough.