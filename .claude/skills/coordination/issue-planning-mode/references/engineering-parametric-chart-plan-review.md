# Engineering Parametric Chart Plan Review

Use this reference when planning or reviewing GitHub issues that request engineering calculations over sweeps (current speed, heading, rudder angle, environmental direction, load case, etc.) plus interactive charts.

## Why this exists

A 2026-05 Sirocco/current-force chart task exposed a recurring planning risk: chart/UI requirements can look straightforward while hiding engineering-contract ambiguities. In that case the requested current sweep was discrete (`1.0` to `4.5` kn), the UI default was `4.56` kn, and the plotted dimensions mixed heading/rudder sweeps with current-speed selection. A good plan must make these contracts explicit before implementation.

## Mandatory plan checks

1. **Freeze coordinate frames before formulas**
   - State the vessel/body axes used for force components (`Fx`, `Fy`, `Mz`, etc.).
   - State sign conventions for heading, current direction, and rudder angle.
   - State whether inputs are relative-to-vessel, earth/global, or reported-source frames.
   - Include at least one test that verifies frame transform/sign convention behavior.

2. **Separate engineering sweep rows from UI defaults**
   - List the exact requested engineering grid values.
   - If a UI default is off-grid (example: default `4.56 kn` while sweep ends at `4.5 kn`), explicitly choose one:
     - add the default as an extra computed/selectable case;
     - interpolate from the sweep; or
     - default to the nearest computed case and label it clearly.
   - Add tests for the selected behavior.

3. **Do not let representative traces hide required coverage**
   - If charts show a subset for readability, document which slices are representative and where the full table/JSON coverage lives.
   - Prefer two interpretable chart families when there are three dimensions:
     - heading sweep at fixed/selected current, faceted or colored by rudder angle; and
     - rudder sweep at fixed/selected current, faceted or colored by heading.
   - Ensure the dropdown selection updates both charts from the same data source.

4. **Define the chart contract as data + UI behavior**
   - Required artifacts should include machine-readable data (CSV/JSON) and rendered HTML.
   - Plan tests should assert:
     - row count equals `len(currents) * len(headings) * len(rudder_angles)` plus any declared off-grid/default cases;
     - all requested parameter values are present;
     - chart/dropdown config references the same current-speed keys as the data;
     - displayed units are explicit.

5. **Use placeholder concept charts in the plan**
   - Include text/pseudocode or lightweight sketches showing axes, dropdown behavior, and chart grouping.
   - Mark them as placeholders unless generated from real calculations.

## Pseudocode skeleton

```python
currents_kn = [1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5]
headings_deg = range(-10, 11, 1)
rudder_deg = range(-10, 11, 1)
default_current_kn = 4.56

if default_current_kn not in currents_kn:
    currents_for_ui = sorted(set(currents_kn + [default_current_kn]))  # or document interpolation/nearest
else:
    currents_for_ui = currents_kn

rows = []
for current in currents_for_ui:
    for heading in headings_deg:
        for rudder in rudder_deg:
            force_body = compute_force_components(
                current_kn=current,
                heading_deg=heading,
                rudder_deg=rudder,
                frame="body",
            )
            rows.append({
                "current_kn": current,
                "heading_deg": heading,
                "rudder_deg": rudder,
                "fx": force_body.fx,
                "fy": force_body.fy,
                "mz": force_body.mz,
            })

write_csv_json(rows)
write_html_dropdown_charts(rows, default_current_kn=default_current_kn)
```

## Review failure patterns

Return `MAJOR` during plan review if any of these are true:
- formula/sign conventions are missing for force components;
- off-grid default values are not acknowledged;
- row-count/value-coverage tests are absent;
- charts only show a hand-picked subset with no full-data artifact;
- the plan implies implementation before user approval or before TDD tests.
