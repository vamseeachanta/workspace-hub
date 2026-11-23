# Parameter-Sweep HTML Report Review Pattern

Use this reference when reviewing engineering HTML reports that visualize generated parameter sweeps (for example current speed × heading × rudder angle).

## Review checklist

1. Load the report through a local HTTP server rather than `file://` so external/local scripts behave normally.
2. Check browser console for JavaScript errors before judging visuals.
3. Verify controls from DOM:
   - dropdown IDs and labels are present;
   - option values match requested engineering cases;
   - selected defaults match the user/requested default;
   - any extra default case is explicitly labeled.
4. Verify data contract from the source artifact, not only from the chart:
   - source row count;
   - unique sweep values;
   - first/last values and step count for each axis;
   - rows per selected grouping (e.g., rows per current speed);
   - requested rows vs extra default rows when applicable.
5. Exercise interaction:
   - change the primary dropdown;
   - change any secondary dropdown;
   - verify chart titles or trace data update.
6. Run a visual scan/screenshot:
   - controls visible and unclipped;
   - charts rendered, legible, and not blank;
   - legends/colorbars/axis titles visible;
   - no horizontal overflow at desktop width.
7. For engineering approximations, verify scope/provenance caveats are visible in the report. Flag if the title suggests total physical load while the model only reports a component/subset.

## Plotly DOM note

Depending on Plotly version and render path, rendered chart containers may have `.js-plotly-plot` rather than `.plotly-graph-div`. Count both selectors:

```js
document.querySelectorAll('.js-plotly-plot, .plotly-graph-div').length
```

## Verdict format

Report:
- PASS/FAIL;
- artifact path/URL;
- console status;
- data cardinality verified;
- interaction tested;
- visual findings;
- minor recommendations separated from blockers.
